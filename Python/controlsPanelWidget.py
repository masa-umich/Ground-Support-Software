from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants
from telemParse import TelemParse


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

        self.parser = TelemParse()
        self.sensor_channels = [item for item in self.parser.items if (item != 'zero' and item != '')]
        self.valve_channels = [str(x) for x in range(0, 10)]  # TODO: Connect this to something meaningful

        # Keeps track of all the objects currently being edited
        self.object_editing = None

        # Defines placement and size of control panel
        self.left = self.gui.screenResolution[0] - self.parent.panel_width
        self.top = 0

        self.width = self.parent.panel_width
        self.height = self.gui.screenResolution[1]
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Sets color of control panel
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.darkGray)
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
        self.edit_frame.resize(300 * self.gui.pixel_scale_ratio[0], self.gui.screenResolution[1])
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
        self.sensor_type_textbox = QLineEdit(self)
        self.board_combobox = QComboBox(self)
        self.channel_combobox = QComboBox(self)
        self.serial_number_visibility_group = QButtonGroup(self)
        
        # fonts
        title_font = QFont()
        title_font.setBold(True)
        title_font.setUnderline(True)
        title_font.setPointSize(13 * self.gui.font_scale_ratio)

        self.default_font = QFont()
        self.default_font.setPointSize(13 * self.gui.font_scale_ratio)

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
                            ["Undefined"] + Constants.boards)  # TODO: Instead of allowing all boards, only allow boards that are currently configured
        self.createComboBox(self.channel_combobox, "Channel", "Channel:",
                            ["Undefined"] + self.sensor_channels)
        self.createLineEdit(self.sensor_type_textbox, "Sensor Units", "Sensor Units:") #["Static Pressure", "Differential Pressure", "Temperature", "Force", "Valve Position"]
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
        # Row 14
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

        if value:
            trueButton.setChecked(True)
            falseButton.setChecked(False)
        else:
            trueButton.setChecked(False)
            falseButton.setChecked(True)

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

    def updateEditPanelFields(self, object_):
        """
        Updates the various fields in the edit frame when a new object is selected for editing
        :param object_: the object that is selected for editing
        """

        # Updates the available values for the channels for solenoids and generic sensors
        if object_.object_name == "Solenoid" or object_.object_name == "3 Way Valve":
            self.comboBoxReplaceFields(self.channel_combobox, ["Undefined"] + self.valve_channels)
        elif object_.object_name == "Generic Sensor":
            self.comboBoxReplaceFields(self.channel_combobox, ["Undefined"] + self.sensor_channels)

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

        # Enables the board and channel box and sets there values
        if object_.object_name == "Generic Sensor" or object_.object_name == "Solenoid" or object_.object_name == "3 Way Valve":
            self.channel_combobox.setEnabled(True)
            self.channel_combobox.setCurrentText(object_.channel)
            self.board_combobox.setEnabled(True)
            self.board_combobox.setCurrentText(object_.avionics_board)
        else:
            self.channel_combobox.setDisabled(True)
            self.board_combobox.setDisabled(True)

        # Enables the units box and sets it value
        if object_.object_name == "Generic Sensor":
            self.sensor_type_textbox.setEnabled(True)
            self.sensor_type_textbox.setText(object_.units)
        else:
            self.sensor_type_textbox.setDisabled(True)

    def updateEditingObjectFields(self, text, identifier):
        """
        Called when user changes field of an object from the edit panel
        :param text: Text of field that is being changed
        :param identifier: identifier of the field being changed
        """
        # Gets the object being edited right now and updated the fields based on identifier
        object_ = self.object_editing # Lazy mans fix

        # Sanity check that object is actually being edited
        if object_.is_being_edited:

            # Component Parameters
            if identifier == "Component Name":
                object_.setLongName(text)
            elif identifier == "Serial Number":
                object_.setShortName(text)
            elif identifier == "Component Fixed?":
                object_.setPositionLock(text)
            elif identifier == "Component Scale":
                object_.setScale(text)
            elif identifier == "Component Fluid":
                object_.setFluid(text)
            elif identifier == "Board":
                object_.setAvionicsBoard(text)
            elif identifier == "Channel":
                object_.setChannel(text)
            elif identifier == "Sensor Units" and object_.object_name == "Generic Sensor":
                object_.setUnits(text)

            # Component Label Parameters
            elif identifier == "Component Name Visibility":
                object_.long_name_label.setVisible(text)
            elif identifier == "Component Name Position":
                object_.long_name_label.moveToPosition(text)
            elif identifier == "Component Name Font Size":
                object_.long_name_label.setFontSize(text)
            elif identifier == "Component Name Rows":
                object_.long_name_label.setRows(text)

            # Serial Number Label Parameters
            elif identifier == "Serial Number Visibility":
                object_.serial_number_label.setVisible(text)
            elif identifier == "Serial Number Position":
                object_.serial_number_label.moveToPosition(text)
            elif identifier == "Serial Number Font Size":
                object_.serial_number_label.setFontSize(text)

    # HMM: Move is_being_edited to object class and call this function here
    def addEditingObject(self, object_):
        """
        Adds object to list to be edited
        """
        # Make sure the currently editing object is removed
        self.removeEditingObject()
        # Keep track of what object is being updated, and update the fields
        object_.setIsEditing(True)
        self.object_editing = object_
        self.edit_frame.show()
        self.updateEditPanelFields(object_)

    def removeEditingObject(self):
        """
        Removes object from list to be edited
        """
        # Safely remove the object that is currently being edited
        if self.object_editing is not None:
            self.object_editing.setIsEditing(False)
            self.object_editing = None
            self.edit_frame.hide()