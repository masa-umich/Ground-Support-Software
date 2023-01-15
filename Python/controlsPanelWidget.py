from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants
import traceback
from overrides import overrides


class ControlsPanelWidget(QWidget):
    """
    Widget that contains controls that are not through icons on screen. Ex. Editing, Arming etc
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.window = parent.window
        # TODO: Rename the controls because it is weird
        self.controls = self.parent.controlsWidget

        self.gui = self.parent.gui
        self.interface = self.window.interface

        self.painter = QPainter()

        # Keeps track of the differnt channels in boxes
        self.sensor_channels = self.interface.channels
        self.valve_channels = []
        self.motor_channels = []
        self.tank_channels = []

        # Keeps track of all the objects currently being edited
        self.editing_object_list = []
        self.object_editing = None

        # Defines placement and size of control panel
        self.left = self.gui.screenResolution[0] - self.parent.panel_width
        self.top = 0

        self.width = self.parent.panel_width
        self.height = self.parent.height
        self.setGeometry(int(self.left), int(self.top), int(self.width), int(self.height))

        # Sets color of control panel
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(66, 66, 66))
        self.setPalette(p)
        
        # Inits widgets for edit frame
        self.initEditFrame()

        self.hide()

    def initEditFrame(self):
        """
        Inits the widgets inside of the editing frame
        """
        # Frames and layouts that holds everything in it and can be hidden / shown
        self.edit_frame = QFrame(self)
        self.edit_form_layout = QFormLayout(self)
        self.edit_form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.edit_frame.resize(int(300 * self.gui.pixel_scale_ratio[0]), int(self.gui.screenResolution[1]))
        self.edit_frame.setLayout(self.edit_form_layout)

        # Textboxes, radioButtons, and drop-downs
        self.component_name_textbox = QLineEdit(self)
        self.long_name_visibility_group = QButtonGroup(self)  # Not really needed here but including it
        self.is_pos_locked_group = QButtonGroup  # Used for radio buttons
        self.long_name_position_combobox = QComboBox(self)
        self.long_name_font_size_spinbox = QDoubleSpinBox(self)
        self.long_name_row_spinbox = QDoubleSpinBox(self)
        self.fluid_combobox = QComboBox(self)
        self.serial_number_textbox = QLineEdit(self)
        self.serial_number_position_combobox = QComboBox(self)
        self.serial_number_font_size_spinbox = QDoubleSpinBox(self)
        self.scale_spinbox = QDoubleSpinBox(self)
        self.board_combobox = QComboBox(self)
        self.channel_combobox = QComboBox(self)
        self.serial_number_visibility_group = QButtonGroup(self)
        self.solenoid_NC_NO_combobox = QComboBox(self)
        self.solenoid_keybind = QLineEdit(self)
        
        # fonts
        title_font = QFont()
        title_font.setBold(True)
        title_font.setUnderline(True)
        title_font.setPointSize(int(13 * self.gui.font_scale_ratio))

        self.default_font = QFont()
        self.default_font.setPointSize(int(13 * self.gui.font_scale_ratio))

        # Component Parameters
        label = QLabel("Component Parameters:                                                                  ") # TODO: jankity jank jank
        label.setFont(title_font)
        label.setStyleSheet("color: white")
        self.edit_form_layout.addRow(label)
        self.createLineEdit(self.component_name_textbox, "Component Name", "Component Name:")
        self.createLineEdit(self.serial_number_textbox, "Serial Number", "Serial Number:")
        self.is_pos_locked_group = self.createTFRadioButtons("Component Fixed?", "Position:", "Locked", "Unlocked", False)
        self.createSpinbox(self.scale_spinbox, "Component Scale", "Scale:", .1, 10, 0.1)
        self.createComboBox(self.fluid_combobox, "Component Fluid", "Fluid:", Constants.fluids)
        self.createComboBox(self.board_combobox, "Board", "Board:",
                            ["Undefined"] + Constants.boards)
        self.createComboBox(self.channel_combobox, "Channel", "Channel:",
                            ["Undefined"] + self.sensor_channels)
        self.channel_combobox.setEditable(True)
        completer = QCompleter(self.sensor_channels)
        completer.setCaseSensitivity(False)
        self.channel_combobox.setCompleter(completer)
        self.channel_combobox.setStyleSheet("QComboBox { combobox-popup: 0; }");
        self.channel_combobox.setMaxVisibleItems(8)
        self.edit_form_layout.addRow(QLabel(""))

        # Component Label Parameters
        label = QLabel("Component Name Label:                                                                  ")
        label.setFont(title_font)
        label.setStyleSheet("color: white")
        self.edit_form_layout.addRow(label)
        self.long_name_visibility_group = self.createTFRadioButtons("Component Name Visibility", "Visibility:", "Shown", "Hidden", True)
        self.createComboBox(self.long_name_position_combobox, "Component Name Position", "Position:", ["Top","Right","Bottom","Left", "Custom"])
        self.createSpinbox(self.long_name_font_size_spinbox, "Component Name Font Size", "Font Size:", 6, 50, 1)
        self.createSpinbox(self.long_name_row_spinbox, "Component Name Rows", "Text Rows:", 1, 5, 1)
        self.edit_form_layout.addRow(QLabel(""))

        # Serial Label Parameters
        label = QLabel("Serial Number Label:                                                                  ")
        label.setFont(title_font)
        label.setStyleSheet("color: white")
        self.edit_form_layout.addRow(label)
        self.serial_number_visibility_group = self.createTFRadioButtons("Serial Number Visibility", "Visibility:", "Shown", "Hidden", True)
        self.createComboBox(self.serial_number_position_combobox, "Serial Number Position","Position:", ["Top", "Right", "Bottom", "Left", "Custom"])
        self.createSpinbox(self.serial_number_font_size_spinbox, "Serial Number Font Size","Font Size:", 6, 50, 1)
        self.edit_form_layout.addRow(QLabel(""))
        # Row 14

        # Specific Parameters for Solenoids
        self.component_prop_label = QLabel("Component Properties:                                                                  ")
        self.component_prop_label.setFont(title_font)
        self.component_prop_label.setStyleSheet("color: white")
        self.edit_form_layout.addRow(self.component_prop_label)
        self.createComboBox(self.solenoid_NC_NO_combobox, "Solenoid NOvNC", "Coil Type", ["Normally Closed", "Normally Open"])
        self.createLineEdit(self.solenoid_keybind, "Solenoid Keybind", "Keybind:")

        # Specific Parameters for Tanks (allowing press tank without yellow system indicator light)
        self.tank_override_label = QLabel("Component Properties:                                                                  ")
        self.tank_override_label.setFont(title_font)
        self.tank_override_label.setStyleSheet("color: white")
        self.edit_form_layout.addRow(self.tank_override_label)
        self.createCheckbox(self.tank_override_checkbox, "Tank Override", "Override Systems Indicator Light")

        self.edit_frame.hide()

    def createLineEdit(self, lineEdit: QLineEdit, identifier, label_text: str, validator: QValidator = None):
        """
        Creates text box user can type in, used for editing labels and so forth
        :param lineEdit: reference to line edit widget
        :param label_text: label used for the field
        :param identifier: identifies line edit widget, used when text changes
        :param validator: validator used to make sure text entered is int, double etc.
        """
        identifier_label = QLabel(label_text)
        identifier_label.setStyleSheet("color: white")
        identifier_label.setFont(self.default_font)

        lineEdit.textChanged.connect(lambda : self.updateEditingObjectFields(lineEdit.text(), identifier))
        lineEdit.setFont(self.default_font)
        if validator is not None:
            lineEdit.setValidator(validator)

        self.edit_form_layout.addRow(identifier_label, lineEdit)

    # TODO: Make this cleaner, kinda messy right now
    def createTFRadioButtons(self, identifier, label_text: str, true_btn_label = "True", false_btn_label = "False", checked: bool = True):
        """
        Creates two radio buttons to enable/disable aspects of the controls widget
        :param identifier: identifies radioButton widget, used when button is toggled
        :param label_text: label used for the field
        :param true_btn_label: label on the button that correlates to True
        :param false_btn_label: label on the button that correlates to False
        :param checked: Which button, True or False, is initially checked

        :return group: Returns the group holding the true/false buttons, true is always first button
        """
        identifier_label = QLabel(label_text)
        identifier_label.setStyleSheet("color: white")
        identifier_label.setFont(self.default_font)

        group = QButtonGroup(self)

        hbox = QHBoxLayout()
        true_button = QRadioButton(true_btn_label)
        false_button = QRadioButton(false_btn_label)

        true_button.setFont(self.default_font)
        false_button.setFont(self.default_font)

        p = true_button.palette()
        p.setColor(QPalette.Button, Qt.red)
        true_button.setPalette(p)

        if checked:
            true_button.setChecked(True)
        else:
            false_button.setChecked(True)

        group.addButton(true_button)
        group.addButton(false_button)

        true_button.toggled.connect(lambda: self.updateEditingObjectFields(True, identifier))
        false_button.toggled.connect(lambda: self.updateEditingObjectFields(False, identifier))

        hbox.addWidget(true_button)
        hbox.addWidget(false_button)
        hbox.addStretch()

        self.edit_form_layout.addRow(identifier_label, hbox)
        return group

    @staticmethod
    def setTFRadioButtonValue(group: QButtonGroup, value: bool):
        """
        Allows the TF radio buttons to be updated properly when the user switches objects
        :param group: group holding the TF radio buttons, True value is first
        :param value: value the TF button is being set to
        """

        trueButton = group.buttons()[0]
        falseButton = group.buttons()[1]

        trueButton.blockSignals(True)
        falseButton.blockSignals(True)

        if value:
            trueButton.setChecked(True)
            falseButton.setChecked(False)
        else:
            trueButton.setChecked(False)
            falseButton.setChecked(True)

        trueButton.blockSignals(False)
        falseButton.blockSignals(False)

    def createComboBox(self, comboBox: QComboBox, identifier: str, label_text: str, items: []):
        """
        Creates a drop-down box for user selection
        :param comboBox: reference to combobox
        :param identifier: identifies comboBox widget, used when comboBox index changes
        :param label_text: label used for the field
        :param items: list of strings user can select in drop-down
        """
        identifier_label = QLabel(label_text)
        identifier_label.setStyleSheet("color: white")
        identifier_label.setFont(self.default_font)
        
        #I removed this so that I could use sizeHint() method on comboboxes in control panel
        #comboBox.setFixedWidth(100)
        comboBox.addItems(items)
        comboBox.setFont(self.default_font)
        comboBox.currentIndexChanged.connect(lambda: self.updateEditingObjectFields(comboBox.currentText(), identifier))

        self.edit_form_layout.addRow(identifier_label, comboBox)

        comboBox.resize(comboBox.sizeHint())

    @staticmethod
    def comboBoxReplaceFields(comboBox: QComboBox, items: []):
        """
        Takes in a combo box and replaces the current fields with new fields
        :param comboBox: Combo box to perform action on
        :param items: new list of fields
        """

        # When clear and items are called, the combobox is updated so it calls currentIndexChanged, as a result this
        # triggers the updateEditingObjectFields function and overwrites the value for the combobox that is being
        # replaced. As a result we need to block all signals from it temporarily to perform the action
        comboBox.blockSignals(True)

        # Replace the fields
        comboBox.clear()
        comboBox.addItems(items)

        # Enable signals again
        comboBox.blockSignals(False)

    def createSpinbox(self, spinBox: QSpinBox, identifier: str, label_text: str, min:int = 0, max:int = 100, step:float = 1):
        """
        Creates a spinbox, contains a value that can be increased with arrows
        :param spinBox: reference to spinbox
        :param identifier: identifies spinBox widget, used when comboBox index changes
        :param label_text: label used for the field
        :param min: min value allowed in the combo box
        :param max: max value allowed in the combo box
        :param step: amount value increases or decreases by then the arrows are used
        """
        identifier_label = QLabel(label_text)
        identifier_label.setStyleSheet("color: white")
        identifier_label.setFont(self.default_font)

        spinBox.setMinimum(min)
        spinBox.setMaximum(max)
        spinBox.setSingleStep(step)
        spinBox.setFont(self.default_font)

        spinBox.valueChanged.connect(lambda: self.updateEditingObjectFields(spinBox.value(), identifier))

        self.edit_form_layout.addRow(identifier_label, spinBox)

    def createCheckbox(self, checkBox: QCheckBox, identifier: str, label_text: str):
        """
        Creates a checkbox
        :param checkBox: reference to checkbox
        :param identifier: indentifies checkBox widget, used when checkBox index changes
        :param label_text: label used for the box
        """

        # not necessary bc box has it's own text attribute
        # identifier_label = QLabel(label_text)
        # identifier_label.setStyleSheet("color: white")
        # identifier_label.setFont(self.default_font)

        checkBox.setFont(self.default_font)
        checkBox.setText(label_text)

        checkBox.stateChanged.connect(lambda: self.updateEditingObjectFields(str(checkBox.isChecked()), identifier))

        # self.edit_form_layout.addRow(identifier_label, checkBox)
        self.edit_form_layout.addRow(checkBox)

    def blockAllEditPanelFieldSignals(self):
        """
        Block all signals from being emitted from edit panel fields, useful for making changes with no ripple effects
        """

        numRows = self.edit_form_layout.count()

        # For all the items in the layout, block the signals
        for i in range(numRows):
            widget = self.edit_form_layout.itemAt(i).widget()
            if widget is not None:
                widget.blockSignals(True)

    def enableAllEditPanelFieldSignals(self):
        """
        Enable all signals from being emitted from edit panel fields, to undo the block all
        """

        numRows = self.edit_form_layout.count()

        # For all the items in the layout, block the signals
        for i in range(numRows):
            widget = self.edit_form_layout.itemAt(i).widget()
            if widget is not None:
                widget.blockSignals(False)

    def updateEditPanelFields(self, object_):
        """
        Updates the various fields in the edit frame when a new object is selected for editing
        :param object_: the object that is selected for editing
        """

        self.blockAllEditPanelFieldSignals()
        self.hideAllComponentProperties()
        # Updates the available values for the channels for solenoids and generic sensors
        try:
            if not hasattr(object_, "avionics_board"):
                board_name = None
            else:
                board_name = object_.avionics_board

            if board_name in Constants.boards:
                addr = self.interface.getBoardAddr(board_name)
                self.valve_channels = [str(x) for x in range(0, self.interface.num_valves[addr])]
                self.motor_channels = [str(x) for x in range(0, self.interface.num_motors[addr])]
                self.tank_channels = [str(x) for x in range(0, self.interface.num_tanks[addr])]
            else:
                self.valve_channels = []
                self.motor_channels = []
                self.tank_channels = []

            if object_.object_name == "Solenoid" or object_.object_name == "3 Way Valve":
                self.comboBoxReplaceFields(self.channel_combobox, ["Undefined"] + self.valve_channels)
                self.channel_combobox.setEditable(False)
                self.setSolenoidComponentPropertiesVisibility(True)
            elif object_.object_name == "Motor":
                self.comboBoxReplaceFields(self.channel_combobox, ["Undefined"] + self.motor_channels)
                self.channel_combobox.setEditable(False)
            elif object_.object_name == "Tank":
                self.comboBoxReplaceFields(self.channel_combobox, ["Undefined"] + self.tank_channels)
                self.channel_combobox.setEditable(False)
                self.setTankOverridePropertyVisibility(True)
            elif object_.object_name == "Generic Sensor":
                if board_name in Constants.boards:
                    prefix = self.interface.getPrefix(board_name)
                    specific_channels = [i for i in self.sensor_channels if i.startswith(prefix)]
                else:
                    specific_channels = []

                self.comboBoxReplaceFields(self.channel_combobox, ["Undefined"] + specific_channels)
                self.channel_combobox.setEditable(True)
                completer = QCompleter(specific_channels)
                completer.setCaseSensitivity(False)
                self.channel_combobox.setCompleter(completer)
            else:
                self.channel_combobox.setEditable(False)
        except Exception as e:
            print(traceback.format_exc())
            # print("UpdateEditPanelFields Threw Exception")
            # print(e)
            pass

        self.component_name_textbox.setText(object_.long_name)
        self.long_name_position_combobox.setCurrentText(object_.long_name_label.position_string)
        self.setTFRadioButtonValue(self.long_name_visibility_group, object_.long_name_label.isVisible())
        self.setTFRadioButtonValue(self.serial_number_visibility_group, object_.serial_number_label.isVisible())
        self.setTFRadioButtonValue(self.is_pos_locked_group, object_.position_locked)
        self.fluid_combobox.setCurrentText(Constants.fluid[object_.fluid])
        self.serial_number_textbox.setText(object_.serial_number)
        self.serial_number_position_combobox.setCurrentText(object_.serial_number_label.position_string)
        self.scale_spinbox.setValue(object_.scale)
        self.long_name_row_spinbox.setValue(object_.long_name_label.rows)
        self.long_name_font_size_spinbox.setValue(object_.long_name_label.getFontSize())
        self.serial_number_font_size_spinbox.setValue(object_.serial_number_label.getFontSize())

        # Enables the board and channel box and sets their values
        if object_.object_name == "Generic Sensor" or object_.object_name == "Solenoid" or object_.object_name == "3 Way Valve" or object_.object_name == "Motor" or object_.object_name == "Tank":
            self.channel_combobox.setEnabled(True)
            self.channel_combobox.setCurrentText(object_.channel)
            self.board_combobox.setEnabled(True)
            self.board_combobox.setCurrentText(object_.avionics_board)
        else:
            self.channel_combobox.setDisabled(True)
            self.board_combobox.setDisabled(True)

        if object_.object_name == "Solenoid" or object_.object_name == "3 Way Valve":
            self.solenoid_NC_NO_combobox.setCurrentIndex(object_.normally_open)
            self.solenoid_keybind.setText(str(object_.keybind))

        self.enableAllEditPanelFieldSignals()

    def updateEditingObjectFields(self, text, identifier):
        """
        Called when user changes field of an object from the edit panel
        :param text: Text of field that is being changed
        :param identifier: identifier of the field being changed
        """
        # Gets the object being edited right now and updated the fields based on identifier
        object_ = self.object_editing  # Lazy mans fix

        # Sanity check that object is actually being edited
        if object_.is_being_edited:

            # Component Parameters
            if identifier == "Component Name":
                for object_ in self.editing_object_list:
                    object_.setLongName(text)
            elif identifier == "Serial Number":
                object_.setShortName(text)
            elif identifier == "Component Fixed?":
                for object_ in self.editing_object_list:
                    object_.setPositionLock(text)
            elif identifier == "Component Scale":
                for object_ in self.editing_object_list:
                    object_.setScale(text)
            elif identifier == "Component Fluid":
                for object_ in self.editing_object_list:
                    object_.setFluid(text)
            elif identifier == "Board":
                for object_ in self.editing_object_list:
                    if object_.avionics_board != text:
                        object_.setChannel("Undefined")
                    object_.setAvionicsBoard(text)
                self.updateEditPanelFields(object_) # lazy fix for valve numbers
            elif identifier == "Channel":
                object_.setChannel(text)

            # Component Label Parameters
            elif identifier == "Component Name Visibility":
                for object_ in self.editing_object_list:
                    object_.long_name_label.setVisible(text)
                    self.gui.setStatusBarMessage(
                        object_.object_name + "(" + object_.long_name + ")" + ": set component name visible to " + str(text))
            elif identifier == "Component Name Position":
                for object_ in self.editing_object_list:
                    object_.long_name_label.moveToPosition(text)
                    self.gui.setStatusBarMessage(
                        object_.object_name + "(" + object_.long_name + ")" + ": set component name position to " + str(text))
            elif identifier == "Component Name Font Size":
                for object_ in self.editing_object_list:
                    object_.long_name_label.setFontSize(text)
                    self.gui.setStatusBarMessage(
                        object_.object_name + "(" + object_.long_name + ")" + ": set component name font size to " + str(text))
            elif identifier == "Component Name Rows":
                for object_ in self.editing_object_list:
                    object_.long_name_label.setRows(text)
                    self.gui.setStatusBarMessage(
                        object_.object_name + "(" + object_.long_name + ")" + ": set component name rows to " + str(text))

            # Serial Number Label Parameters
            elif identifier == "Serial Number Visibility":
                for object_ in self.editing_object_list:
                    object_.serial_number_label.setVisible(text)
                    self.gui.setStatusBarMessage(
                        object_.object_name + "(" + object_.long_name + ")" + ": serial number visibility to " + str(text))
            elif identifier == "Serial Number Position":
                for object_ in self.editing_object_list:
                    object_.serial_number_label.moveToPosition(text)
                    self.gui.setStatusBarMessage(
                        object_.object_name + "(" + object_.long_name + ")" + ": serial number position to " + str(text))
            elif identifier == "Serial Number Font Size":
                for object_ in self.editing_object_list:
                    object_.serial_number_label.setFontSize(text)
                    self.window.setStatusBarMessage(
                        object_.object_name + "(" + object_.long_name + ")" + ": serial number font size to " + str(text))

            # Custom Parameters for Solenoid
            elif identifier == "Solenoid NOvNC":
                for object_ in self.editing_object_list:
                    if text == "Normally Open":
                        object_.normally_open = True
                    else:
                        object_.normally_open = False

            # Custom Parameters for Tank
            elif identifier == "Tank Override":
                for object_ in self.editing_object_list:
                    if text == "True":
                        object_.override_indicator = True
                    else:
                        object_.override_indicator = False

            elif identifier == "Solenoid Keybind":
                for object_ in self.editing_object_list:
                    object_.keybind = text
            object_.updateToolTip()

    # def doesFormLayoutHaveFocus(self):
    #     numRow = self.edit_form_layout.count()
    #     for i in range(numRow):
    #         widget = self.edit_form_layout.itemAt(i).widget()
    #
    #         if widget is not None and self.edit_form_layout.itemAt(i).widget().hasFocus():
    #             return True
    #
    #     return False

    # HMM: Move is_being_edited to object class and call this function here
    def addEditingObject(self, object_):
        """
        Adds object to list to be edited
        """
        # Check if shift is being pressed, if so add the object to the array of objects being edited
        mod = QApplication.keyboardModifiers()
        if mod == Qt.ShiftModifier:
            if object_ not in self.editing_object_list:
                self.editing_object_list.append(object_)
            object_.setIsEditing(True)
        else:
            # Make sure the currently editing object is removed, and the new object is added
            self.removeAllEditingObjects()
            if object_ not in self.editing_object_list:
                self.editing_object_list.append(object_)
            object_.setIsEditing(True)

        self.setEditingObjectFocus(object_)

    def setEditingObjectFocus(self, object_):
        """
        Sets the specified object as focuses, making sure to have this object data displayed in the panel
        :param object_: object to be set as the focus
        """

        object_.button.setFocus()
        self.object_editing = object_
        self.edit_frame.show()
        self.updateEditPanelFields(object_)

    def removeEditingObject(self, object_):
        """
        Removes object from list to be edited
        """
        object_.setIsEditing(False)
        self.editing_object_list.remove(object_)

    def removeAllEditingObjects(self):
        """
        Removes all the currently editing objects
        """
        for obj in reversed(self.editing_object_list):
            self.removeEditingObject(obj)

        self.object_editing = None
        self.edit_frame.hide()

    def removeOtherEditingObjects(self, object_):
        """
        Removes all but the specified the editing objects
        """
        for obj in reversed(self.editing_object_list):
            if obj is not object_:
                self.removeEditingObject(obj)

        self.setEditingObjectFocus(object_)

    def hideAllComponentProperties(self):
        """
        Hides all the component properties
        """
        self.setSolenoidComponentPropertiesVisibility(False)
        self.setTankOverridePropertyVisibility(False)

    def setSolenoidComponentPropertiesVisibility(self, is_vis):
        """
        Shows the solenoid specific options
        :param is_vis:
        """
        sol_NC_NO_index = self.edit_form_layout.getWidgetPosition(self.solenoid_NC_NO_combobox)
        if is_vis:
            self.component_prop_label.show()
            self.solenoid_NC_NO_combobox.show()
            self.solenoid_keybind.show()
            self.edit_form_layout.itemAt(sol_NC_NO_index[0], sol_NC_NO_index[1] - 1).widget().show()
        else:
            self.component_prop_label.hide()
            self.solenoid_NC_NO_combobox.hide()
            self.solenoid_keybind.hide()
            self.edit_form_layout.itemAt(sol_NC_NO_index[0], sol_NC_NO_index[1] - 1).widget().hide()

    def setTankOverridePropertyVisibility(self, is_vis):
        """
        Shows the tank override for systems light indicator (for tanks that are not connected to a board & channel)
        :param is_vis:
        """
        tank_override_index = self.edit_form_layout.getWidgetPosition(self.tank_override_checkbox)
        if is_vis:
            self.tank_override_label.show()
            self.tank_override_checkbox.show()
            self.edit_form_layout.itemAt(tank_override_index[0], tank_override_index[1] - 1).widget().show()
        else:
            self.tank_override_label.hide()
            self.tank_override_checkbox.hide()
            self.edit_form_layout.itemAt(tank_override_index[0], tank_override_index[1] - 1).widget().hide()


    @overrides
    def paintEvent(self, e):
        """
        This event is called automatically in the background by pyQt. It is used to update the drawing on screen
        This function calls the objects own drawing methods to perform the actual drawing calculations
        """
        self.painter.begin(self)

        # This makes the objects onscreen more crisp
        self.painter.setRenderHint(QPainter.HighQualityAntialiasing)

        # Default pen qualities
        pen = QPen()
        pen.setWidth(Constants.line_width)
        pen.setColor(Constants.MASA_Beige_color)
        self.painter.setPen(pen)

        # Draw the bottom border on the widget
        path = QPainterPath()
        # path.moveTo(0, 75 * self.gui.pixel_scale_ratio[1]-1)  # Bottom left corner
        # path.lineTo(self.width, 75 * self.gui.pixel_scale_ratio[1]-1)  # Straight across

        path.moveTo(1, 0)
        path.lineTo(1, self.height)

        self.painter.drawPath(path)

        self.painter.end()