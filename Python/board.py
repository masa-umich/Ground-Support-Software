from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from datetime import datetime

from overrides import overrides
from constants import Constants
from customLabel import CustomLabel
from indicatorLightWidget import IndicatorLightWidget
from enum import Enum

from PyQt5 import QtWidgets


class Board(QWidget):

    object_name = "Board"

    def __init__(self, parent, name: str):
        """
        Initializer for the board objects that go on the right side of the screen
        :param parent: parent widget
        :param name: name of the board
        """
        super().__init__(parent)
        self.controlsSidebarWidget = parent
        self.gui = self.controlsSidebarWidget.gui
        self.window = self.controlsSidebarWidget.window
        self.painter = QPainter()

        # The height value is updated later
        self.setGeometry(0, 0, self.controlsSidebarWidget.width - 30, 200*self.gui.pixel_scale_ratio[1])

        # Set background color to match
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Constants.MASA_Blue_color)
        self.setPalette(p)

        # Define geometric of board
        self.board_pos = QPointF(10*self.gui.pixel_scale_ratio[0], 38*self.gui.pixel_scale_ratio[1])
        self.board_width = 150 * self.gui.pixel_scale_ratio[0]
        # Board height is programmatically set later, initialized here for clarity
        self.board_height = 0 * self.gui.pixel_scale_ratio[1]

        # Temp holder values
        self.name = name
        self.EBatt = 0
        self.amps = 0
        self.state = 0 # Not sure if this is good to start like this
        self.temp = 273
        self.flash = False
        self.LPT = 0 #Last Ping Time
        self.adc_rate = 0
        self.telem_rate = 0

        # Quick error check
        if name not in Constants.boards:
            print(name + " is not a valid board name.")

        # Set the board state mappings based on board name
        if self.name == "Pressurization Controller":
            self.stateMap = {
                -1: "",
                0: "Manual",
                1: "Armed",
                2: "Auto-Press",
                3: "Startup",
                4: "Ignition",
                5: "Hotfire",
                6: "Abort",
                7: "Post",
                8: "Safe",
                9: "IgnitionFail",
                255: "Continue"
            }
            self.stateNum = {
                "": -1,
                "Manual": 0,
                "Armed": 1,
                "Auto-Press": 2,
                "Startup": 3,
                "Ignition": 4,
                "Hotfire": 5,
                "Abort": 6,
                "Post": 7,
                "Safe": 8,
                "IgnitionFail": 9,
                "Continue": 255
            }
            """  TODO fill this out when we figure out other boards' state mappings
            elif self.name == "Engine Controller":
                pass
            elif self.name == "Flight Computer":
                pass
            elif self.name == "Recovery Controller":
                pass
            """
        elif self.name == "GSE Controller":
            self.stateMap = {
                -1: "",
                0: "Manual"
            }
            self.stateNum = {
                "": -1,
                "Manual": 0
            }
        else:  # Should never get to this point
            self.stateMap = {
                -1: "",
                0: "Manual"
            }
            self.stateNum = {
                "": -1,
                "Manual": 0
            }


        # Connection status indicator light
        self.connectionIndicator = IndicatorLightWidget(self, '', 10, "Red", 10, 10, 10, 1)
        self.connectionIndicator.setToolTip("No connection")
        self.connectionIndicator.move(self.width()-self.connectionIndicator.width(), 0)

        # Board name label
        self.name_label = CustomLabel(self, self.gui, text=self.name)
        self.name_label.setFontSize(16)
        self.name_label.setStyleSheet("color: white")
        self.name_label.setFixedHeight(self.connectionIndicator.circle_radius*2)
        self.name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.name_label.move(self.board_pos.x(), self.connectionIndicator.pos().y()+self.connectionIndicator.hBuffer)

        # Set up the data name label
        self.data_frame = QFrame(self)
        self.data_form_layout = QFormLayout(self)
        self.data_frame.resize(self.width() - (self.board_pos.x() + self.board_width)+5*self.gui.pixel_scale_ratio[0],
                                150*self.gui.pixel_scale_ratio[1] - (self.name_label.pos().y() + self.name_label.height()))
        self.data_frame.setLayout(self.data_form_layout)
        self.data_frame.move((self.board_pos.x() + self.board_width)-5*self.gui.pixel_scale_ratio[0],
                             (self.name_label.pos().y() + self.name_label.height())-11*self.gui.pixel_scale_ratio[1])

        # Create the labels for the data form
        self.data_form_layout.setLabelAlignment(Qt.AlignLeft)
        self.data_form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        EBatt_form_label = self.createDataFormLayoutLabel("ebatt:")
        self.Ebatt_label = self.createDataFormLayoutLabel("-")

        amp_form_label = self.createDataFormLayoutLabel("ibatt:")
        self.amp_label = self.createDataFormLayoutLabel("-")

        # temp_form_label = self.createDataFormLayoutLabel("Temp:")
        # self.temp_label = self.createDataFormLayoutLabel("--K")

        flash_form_label = self.createDataFormLayoutLabel("Flash:")
        self.flash_label = self.createDataFormLayoutLabel("-")

        LPT_form_label = self.createDataFormLayoutLabel("LP Time:")
        self.LPT_label = self.createDataFormLayoutLabel("-")

        adcrate_form_label = self.createDataFormLayoutLabel("ADC Rate:")
        self.adcrate_label = self.createDataFormLayoutLabel("-")

        telemrate_form_label = self.createDataFormLayoutLabel("Tx Rate:")
        self.telemrate_label = self.createDataFormLayoutLabel("-")

        # Populate the layout with the above labels
        self.data_form_layout.addRow(EBatt_form_label, self.Ebatt_label)
        self.data_form_layout.addRow(amp_form_label, self.amp_label)
        #self.data_form_layout.addRow(temp_form_label, self.temp_label)
        self.data_form_layout.addRow(flash_form_label, self.flash_label)
        self.data_form_layout.addRow(LPT_form_label, self.LPT_label)
        self.data_form_layout.addRow(adcrate_form_label, self.adcrate_label)
        self.data_form_layout.addRow(telemrate_form_label, self.telemrate_label)

        # State label to go below buttons
        state_form_label = self.createDataFormLayoutLabel("State:")
        self.state_label = self.createDataFormLayoutLabel("Aggressively long string don't change")

        # lame lame to set parent
        state_form_label.setParent(self)
        self.state_label.setParent(self)

        self.state_frame = QFrame(self)
        # Horizontal button layout
        buttonLayout = QHBoxLayout(self.state_frame)

        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.default_font)
        font.setPointSize(9 * self.gui.font_scale_ratio)

        if self.gui.platform == "OSX":
            fwidth = self.width()/5 * .85
        else:
            fwidth = self.width()/5 * .85

        # Create the buttons, make sure there is no default option, and connect to functions
        self.manual_button = QPushButton("Manual")
        self.manual_button.setDefault(False)
        self.manual_button.setAutoDefault(False)
        self.manual_button.clicked.connect(lambda: self.sendBoardState("Manual-Disarm"))
        self.manual_button.setFont(font)
        self.manual_button.setFixedWidth(fwidth)
        self.manual_button.setEnabled(True)

        self.arm_button = QPushButton("Arm")
        self.arm_button.setDefault(False)
        self.arm_button.setAutoDefault(False)
        self.arm_button.clicked.connect(lambda: self.sendBoardState("Arm"))
        self.arm_button.setFont(font)
        self.arm_button.setFixedWidth(fwidth)

        self.fire_button = QPushButton("")
        self.fire_button.setDefault(False)
        self.fire_button.setAutoDefault(False)
        self.fire_button.setDisabled(True)
        self.fire_button.clicked.connect(lambda: self.sendBoardState("Run"))
        self.fire_button.setFont(font)
        self.fire_button.setFixedWidth(fwidth)

        self.continue_button = QPushButton("Cont.")
        self.continue_button.setDefault(False)
        self.continue_button.setAutoDefault(False)
        self.continue_button.setDisabled(False)
        self.continue_button.clicked.connect(lambda: self.sendBoardState("Continue"))
        self.continue_button.setFont(font)
        self.continue_button.setFixedWidth(fwidth)

        self.abort_button = QPushButton("Abort")
        self.abort_button.setDefault(False)
        self.abort_button.setAutoDefault(False)
        self.abort_button.clicked.connect(lambda: self.sendBoardState("Abort"))
        self.abort_button.setFont(font)
        self.abort_button.setFixedWidth(fwidth)
        self.abort_button.setDisabled(True)

        self.rem_timer = QLabel(self)
        if self.name == "Pressurization Controller":
         # Remaining time in state
            rem_timer_font = QFont()
            rem_timer_font.setStyleStrategy(QFont.PreferAntialias)
            rem_timer_font.setFamily(Constants.monospace_font)
            rem_timer_font.setPointSizeF(14 * self.gui.font_scale_ratio)
            self.rem_timer.setFont(rem_timer_font)
            self.rem_timer.setText("00 s")
            self.rem_timer.setStyleSheet("color: white")
            self.rem_timer.show()

        # Set text depending on board
        if self.name == "Engine Controller":
            self.fire_button.setText("Hotfire")
        elif self.name == "Pressurization Controller":
            self.fire_button.setText("Press")
        elif self.name == "Flight Computer":
            self.fire_button.setText("Launch")
        else:
            self.fire_button.setText("Order 66")
        
        # Currently, only the press board has a state machine
        # Other boards will have these buttons disabled
        buttonLayout.addWidget(self.manual_button)
        buttonLayout.addWidget(self.arm_button)
        buttonLayout.addWidget(self.fire_button)
        buttonLayout.addWidget(self.continue_button)
        buttonLayout.addWidget(self.abort_button)

        self.show()  # Need to show before able to access some data_frame values
        self.setBoardState(self.state)

        # Set the board height to be the same size as the text because it looks good
        self.board_height = self.telemrate_label.pos().y() + self.telemrate_label.height() + self.data_frame.y() - self.board_pos.y()

        # Update the frame geometry
        self.state_frame.setGeometry(0, self.board_height + self.board_pos.y(), self.width(), 60*self.gui.pixel_scale_ratio[1])
        # Make sure the buttons don't clip
        if self.state_frame.height() + self.state_frame.y() > self.height() -state_form_label.height():
            self.setFixedHeight(self.state_frame.height() + self.state_frame.y()+state_form_label.height())
        # Move to position, little dirty atm
        state_form_label.move(self.board_pos.x(), self.state_frame.y()+self.state_frame.height() + -8 * self.gui.pixel_scale_ratio[1])
        if self.name == "Pressurization Controller":
            self.rem_timer.move(state_form_label.x() + state_form_label.width()+155, self.state_frame.y()+self.state_frame.height() + -8 * self.gui.pixel_scale_ratio[1])
        self.state_label.move(state_form_label.x()+state_form_label.width()+3, self.state_frame.y()+self.state_frame.height() + -8 * self.gui.pixel_scale_ratio[1])
        self.board_background_button = QPushButton(self)
        self.board_background_button.setGeometry(self.board_pos.x(), self.board_pos.y(), self.board_width,self.board_height)
        self.board_background_button.setStyleSheet("background-color:transparent;border:0;")
        self.board_background_button.clicked.connect(self.onClick)
        self.board_background_button.show()

        self.gui.liveDataHandler.dataPacketSignal.connect(self.updateFromDataPacket)

    def onClick(self):
        print(self.name + " clicked! But doing nothing about it")
        #self.showBoardSettingsDialog()

    # TODO: THIS IS NOT CALLED EVER
    def showBoardSettingsDialog(self):
        """
        Shows a dialog when the motor is clicked. Allows the user to update the set point, zero and PID constants
        """

        # Right now only have settings for press board
        if self.name != "Pressurization Controller":
            return


        # Create the dialog
        dialog = QDialog(self.window)
        dialog.setWindowTitle(self.name + " Settings")
        dialog.setWindowModality(Qt.ApplicationModal)

        # Set dialog size and place in middle of window
        dialog.resize(450 * self.gui.pixel_scale_ratio[0], 240 * self.gui.pixel_scale_ratio[1])
        dialog.setMinimumWidth(450 * self.gui.pixel_scale_ratio[0])
        dialog.setMinimumWidth(240 * self.gui.pixel_scale_ratio[1])
        dialog.move((self.window.width() - dialog.width()) / 2,
                    (self.window.height() - dialog.height()) / 2)

        # Vertical layout to hold everything
        verticalLayout = QVBoxLayout(dialog)

        # Create the form layout that will hold the text box
        formLayout = QFormLayout()
        formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)  # This is properly resize textbox on OSX
        verticalLayout.addLayout(formLayout)

        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.default_font)
        font.setPointSize(14 * self.gui.font_scale_ratio)

        # Create spin boxes
        setPointBox = QDoubleSpinBox()
        setPointBox.setDecimals(1)
        setPointBox.setMinimum(-2999.9)
        setPointBox.setMaximum(2999.9)
        #setPointBox.setValue(self.setPoint)
        setPointBox.setFont(font)

        PPointBox = QDoubleSpinBox()
        PPointBox.setMaximum(599.99)
        #PPointBox.setValue(self.Pconstant)
        PPointBox.setDecimals(2)
        PPointBox.setFont(font)

        IPointBox = QDoubleSpinBox()
        IPointBox.setMaximum(599.99)
        #IPointBox.setValue(self.Iconstant)
        IPointBox.setDecimals(2)
        IPointBox.setFont(font)

        DPointBox = QDoubleSpinBox()
        DPointBox.setMaximum(599.99)
        #DPointBox.setValue(self.Dconstant)
        DPointBox.setDecimals(2)
        DPointBox.setFont(font)


        # Create zero button
        zeroBtn = QPushButton("Zero Now")
        zeroBtn.setDefault(False)
        zeroBtn.setAutoDefault(False)
        #zeroBtn.clicked.connect(self.motorDialogZeroButtonClicked)

        spinBoxes = [setPointBox,PPointBox,IPointBox,DPointBox]

        label1 = QLabel("Set Point:")
        label1.setFont(font)
        label2 = QLabel("P Constant:")
        label2.setFont(font)
        label3 = QLabel("I Constant:")
        label3.setFont(font)
        label4 = QLabel("D Constant:")
        label4.setFont(font)
        label5 = QLabel("Set Zero:")
        label5.setFont(font)

        # Add to the layout
        formLayout.addRow(label1, setPointBox)
        formLayout.addRow(label2, PPointBox)
        formLayout.addRow(label3, IPointBox)
        formLayout.addRow(label4, DPointBox)
        formLayout.addRow(label5, zeroBtn)

        # Horizontal button layout
        buttonLayout = QHBoxLayout()
        # Create the buttons, make sure there is no default option, and connect to functions
        cancel_button = QPushButton("Cancel")
        cancel_button.setFont(font)
        cancel_button.setDefault(False)
        cancel_button.setAutoDefault(False)
        cancel_button.clicked.connect(lambda: dialog.done(1))
        cancel_button.setFixedWidth(125 * self.gui.pixel_scale_ratio[0])  # Lazy way to make buttons not full width

        save_button = QPushButton("Save")
        save_button.setFont(font)
        save_button.setDefault(False)
        save_button.setAutoDefault(False)
        #save_button.clicked.connect(lambda: self.motorDialogSave(spinBoxes, dialog))
        save_button.setFixedWidth(125 * self.gui.pixel_scale_ratio[0])

        buttonLayout.addWidget(cancel_button)
        buttonLayout.addWidget(save_button)

        verticalLayout.addLayout(buttonLayout)

        dialog.show()

    def createDataFormLayoutLabel(self, text: str):
        """
        Quick helper method that creates the labels used for the data of this widget
        :param text: label text
        :return: the label that is created
        """

        label = CustomLabel(None, self.gui, text = text)
        label.setFontSize(13)  # Don't need font size scalar because it is already defined in CustomLabel
        label.setStyleSheet("color: white")

        return label

    def sendBoardState(self, identifier: str):
        """
        Send the board state, if not in debug mode will send to the connected board
        :param identifier: string used to determine state to send
        :return: only returns if a new state can't be found, this is an error but prevents the gui from crashing in
        a critical moment
        """

        newState = None

        # Ask for confirmation for all buttons except for Abort
        if identifier != "Abort":
            dialog = QMessageBox.question(self, '', "Are you sure you want to change the state to " + identifier + "?",
                                          QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if dialog == QtWidgets.QMessageBox.No:
                return

        # If arm/disarmed command is sent toggle, only toggle if state is manual to arm, otherwise always disarm
        if identifier == "Manual-Disarm":
            newState = self.stateNum["Manual"] #0
        elif identifier == "Arm":
            if self.name == "Pressurization Controller":
                cmd_dict = {  # For Pressboard-GSE daisy chain setup: reset system clocks to 0 when armed in case operators forget
                    "function_name": "set_system_clock",
                    "target_board_addr": 3,
                    "timestamp": int(datetime.now().timestamp()),
                    "args": [0]
                }
                self.gui.liveDataHandler.sendCommand(3, cmd_dict)
                cmd_dict = {
                    "function_name": "set_system_clock",
                    "target_board_addr": 0,
                    "timestamp": int(datetime.now().timestamp()),
                    "args": [0]
                }
                self.gui.liveDataHandler.sendCommand(3, cmd_dict)
            newState = self.stateNum["Armed"]
        # If state is armed, allow for state to be run
        elif identifier == "Run":
            if self.state == self.stateNum["Armed"]:  # Push Press to go into Autopress
                newState = self.stateNum["Auto-Press"]
            elif self.state == self.stateNum["Auto-Press"]:  # Push Press again to go into Startup
                newState = self.stateNum["Startup"]
        # Anytime can call an abort to abort out
        elif identifier == "Abort":
            newState = self.stateNum["Abort"]
        elif identifier == "Continue":
            newState = self.stateNum["Continue"]
        else:
            print("Invalid state command given to sendBoardState")
            return

        # If in debug mode don't send and just update
        if self.gui.debug_mode:
            self.setBoardState(newState)
        else:
            cmd_dict = {
                "function_name": "set_state",
                "target_board_addr": self.controlsSidebarWidget.window.interface.getBoardAddr(self.name),
                "timestamp": int(datetime.now().timestamp()),
                "args": [int(newState)]
            }
            self.gui.liveDataHandler.sendCommand(3, cmd_dict)
            #self.setBoardState(newState)
        #if self.name == "Pressurization Controller":
         #   self.controlsSidebarWidget.title_label.setText(self.stateMap[newState])

       # if identifier == "Abort":
       #     self.controlsSidebarWidget.setAutoFillBackground(True)
       #     p = self.controlsSidebarWidget.palette()
      #      p.setColor(self.controlsSidebarWidget.backgroundRole(), Constants.Indicator_Red_color)
       #     self.controlsSidebarWidget.setPalette(p)
      #  else:
      #     self.controlsSidebarWidget.setAutoFillBackground(True)
       #     p = self.controlsSidebarWidget.palette()
       #     p.setColor(self.controlsSidebarWidget.backgroundRole(), Constants.MASA_Blue_color)
       #     self.controlsSidebarWidget.setPalette(p)

    def setBoardState(self, state: int):
        """
        Sets the current board state, updates all the buttons and state labels
        :param state: state to set
        """

        # Set state
        self.state = state

        # Update labels
        self.state_label.setText(self.stateMap[self.state])

        # TODO: not sure what this does???
        if self.name == "Pressurization Controller":
            pass
        elif self.name == "GSE Controller":
            pass
        else:
            print("Invalid board(" + self.name + ") somehow used in Board:setBoardState, it should never get to this point lol. State: " + str(state))
            return

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
        pen.setWidth(Constants.line_width+1)  # Slightly thicker line
        pen.setColor(Constants.Board_color)
        self.painter.setPen(pen)
        path = QPainterPath()

        # Draw the board
        path.moveTo(self.board_pos)
        path.lineTo(self.board_pos.x(), self.board_pos.y() + self.board_height)
        path.lineTo(self.board_pos.x()+self.board_width, self.board_pos.y() + self.board_height)
        path.lineTo(self.board_pos.x()+self.board_width, self.board_pos.y())
        path.lineTo(self.board_pos.x(), self.board_pos.y())

        self.painter.drawPath(path)

        # Default pen qualities
        pen = QPen()
        pen.setWidth(Constants.line_width+2)  # thicker line
        pen.setColor(Qt.black)
        self.painter.setBrush(Qt.NoBrush)
        self.painter.setPen(pen)

        # Base connector diameter
        connector_diam = 10 * self.gui.pixel_scale_ratio[0]

        # Make the connector positions look similar to the real board, not really pretty but wanted to do something
        if self.name == "Flight Computer" or self.name == "Recovery Controller":
            self.painter.drawEllipse(QPointF(self.board_pos.x() + self.board_width * .25,self.board_pos.y()+ self.board_height/2),2.5*connector_diam, 2.5*connector_diam)
        elif self.name == "Pressurization Controller":
            self.painter.drawEllipse(QPointF(self.board_pos.x() + self.board_width * .15, self.board_pos.y() + self.board_height / 2), 1.5 * connector_diam, 1.5 * connector_diam)
            self.painter.drawEllipse(
                QPointF(self.board_pos.x() + self.board_width * .45, self.board_pos.y() + self.board_height / 2),
                1.5 * connector_diam, 1.5 * connector_diam)
            self.painter.drawEllipse(
                QPointF(self.board_pos.x() + self.board_width * .80, self.board_pos.y() + self.board_height / 2),
                1.5 * connector_diam, 1.5 * connector_diam)
        elif self.name == "Engine Controller" or self.name == "GSE Controller":
            self.painter.drawEllipse(QPointF(self.board_pos.x() + self.board_width * .15, self.board_pos.y() + 2*self.board_height / 7), connector_diam, connector_diam)
            self.painter.drawEllipse(QPointF(self.board_pos.x() + self.board_width * .38, self.board_pos.y() + 2*self.board_height / 7), connector_diam, connector_diam)
            self.painter.drawEllipse(QPointF(self.board_pos.x() + self.board_width * .59, self.board_pos.y() + 2*self.board_height / 7), connector_diam, connector_diam)
            self.painter.drawEllipse(QPointF(self.board_pos.x() + self.board_width * .85, self.board_pos.y() + 2*self.board_height / 7), connector_diam, connector_diam)

            self.painter.drawEllipse(QPointF(self.board_pos.x() + self.board_width * .15, self.board_pos.y() + 5*self.board_height / 7), connector_diam, connector_diam)
            self.painter.drawEllipse(QPointF(self.board_pos.x() + self.board_width * .38, self.board_pos.y() + 5*self.board_height / 7), connector_diam, connector_diam)
            self.painter.drawEllipse(QPointF(self.board_pos.x() + self.board_width * .59, self.board_pos.y() + 5*self.board_height / 7), connector_diam, connector_diam)
            self.painter.drawEllipse(QPointF(self.board_pos.x() + self.board_width * .85, self.board_pos.y() + 5*self.board_height / 7), connector_diam, connector_diam)

        # Default pen qualities
        pen = QPen()
        pen.setWidth(Constants.line_width)
        pen.setColor(Constants.MASA_Beige_color)
        self.painter.setPen(pen)
        self.painter.setBrush(Qt.NoBrush)
        path = QPainterPath()

        # Bottom border around the board widget
        path.moveTo(self.width(),self.height()-1)
        path.lineTo(0, self.height()-1)
        path.moveTo(0, 0)
        self.painter.drawPath(path)

        self.painter.end()

    @overrides
    def update(self, ebatt, ibatt, state, flash, LPT, adc_rate, telem_rate, state_rem_time):
        """
        Function to update board state
        :param ebatt: bus voltage
        :param ibatt: bus current
        :param state: board state
        :param flash: flash state
        :param LPT: timestamp of last ping
        :param adc_rate: adc sample rate
        :param telem_rate: telem packet rate
        :return: None
        """

        print(self.size())
        super().update()
        print(self.size())
        self.Ebatt_label.setText(str(ebatt) + " V")
        self.amp_label.setText(str(ibatt) + " A")
        self.setBoardState(int(state))
        self.flash_label.setText(str(flash))  # todo: flash state parsing
        self.LPT_label.setText(str(int((LPT-self.LPT)/1000)) + "ms")
        self.adcrate_label.setText(str(adc_rate) + " Hz")
        self.telemrate_label.setText(str(telem_rate) + " Hz")
        self.rem_timer.setText(str(state_rem_time/1000) + " s")
        if self.name == "Pressurization Controller":
            self.controlsSidebarWidget.title_label.setText(self.stateMap[state])
            #self.controlsSidebarWidget.state_time_label.setText("Rem Time: " + str(state_rem_time/1000) + " s")

        self.LPT = LPT

        # Draw red background in abort state
        if self.name == "Pressurization Controller" and self.state == self.stateNum["Abort"]:
            self.controlsSidebarWidget.setAutoFillBackground(True)
            p = self.controlsSidebarWidget.palette()
            p.setColor(self.controlsSidebarWidget.backgroundRole(), Constants.Indicator_Red_color)
            self.controlsSidebarWidget.setPalette(p)
        else:
            self.controlsSidebarWidget.setAutoFillBackground(True)
            p = self.controlsSidebarWidget.palette()
            p.setColor(self.controlsSidebarWidget.backgroundRole(), Constants.MASA_Blue_color)
            self.controlsSidebarWidget.setPalette(p)

        
        # Disable all GSE state commands
        if self.name == "GSE Controller":
            self.fire_button.setDisabled(True)
            self.continue_button.setDisabled(True)
            self.manual_button.setDisabled(True)
            self.arm_button.setDisabled(True)
            self.abort_button.setDisabled(True)

        # Enable buttons as allowed in the Press board state machine
        elif self.name == "Pressurization Controller":
            if self.state == self.stateNum["Manual"]:
                self.manual_button.setText("Manual")
                self.manual_button.setEnabled(False)
                self.arm_button.setEnabled(True)
                self.fire_button.setEnabled(False)
                self.continue_button.setEnabled(False)
                self.abort_button.setEnabled(False)

            elif self.state == self.stateNum["Armed"]:
                self.manual_button.setText("Disarm")
                self.manual_button.setEnabled(True)
                self.arm_button.setEnabled(False)
                self.fire_button.setEnabled(True)
                self.continue_button.setEnabled(False)
                self.abort_button.setEnabled(False)
                
            elif self.state == self.stateNum["Auto-Press"]:
                self.manual_button.setText("Disarm")
                self.manual_button.setEnabled(True)
                self.arm_button.setEnabled(False)
                self.fire_button.setEnabled(True)
                self.continue_button.setEnabled(False)
                self.abort_button.setEnabled(False)
                
            elif self.state == self.stateNum["Startup"]:
                self.manual_button.setText("Disarm")
                self.manual_button.setEnabled(True)
                self.arm_button.setEnabled(False)
                self.fire_button.setEnabled(False)
                self.continue_button.setEnabled(True)
                self.abort_button.setEnabled(False)

            elif self.state == self.stateNum["Ignition"]:
                self.manual_button.setText("Disarm")
                self.manual_button.setEnabled(False)
                self.arm_button.setEnabled(False)
                self.fire_button.setEnabled(False)
                self.continue_button.setEnabled(False)
                self.abort_button.setEnabled(False)
                
            elif self.state == self.stateNum["Hotfire"]:
                self.manual_button.setText("Disarm")
                self.manual_button.setEnabled(False)
                self.arm_button.setEnabled(False)
                self.fire_button.setEnabled(False)
                self.continue_button.setEnabled(False)
                self.abort_button.setEnabled(False)
                
            elif self.state == self.stateNum["Post"]:
                self.manual_button.setText("Disarm")
                self.manual_button.setEnabled(False)
                self.arm_button.setEnabled(False)
                self.fire_button.setEnabled(False)
                self.continue_button.setEnabled(False)
                self.abort_button.setEnabled(False)
                
            elif self.state == self.stateNum["Safe"]:
                self.manual_button.setText("Disarm")
                self.manual_button.setEnabled(True)
                self.arm_button.setEnabled(False)
                self.fire_button.setEnabled(False)
                self.continue_button.setEnabled(False)
                self.abort_button.setEnabled(False)
                
            elif self.state == self.stateNum["Abort"]:
                self.manual_button.setText("Disarm")
                self.manual_button.setEnabled(True)
                self.arm_button.setEnabled(False)
                self.fire_button.setEnabled(False)
                self.continue_button.setEnabled(False)
                self.abort_button.setEnabled(False)

            elif self.state == self.stateNum["IgnitionFail"]:
                self.manual_button.setText("Disarm")
                self.manual_button.setEnabled(True)
                self.arm_button.setEnabled(False)
                self.fire_button.setEnabled(False)
                self.continue_button.setEnabled(False)
                self.abort_button.setEnabled(False)

        print(self.size())

    @pyqtSlot(object)
    def updateFromDataPacket(self, data_packet: dict):

        prefix = self.gui.controlsWindow.interface.getPrefix(self.name)

        if self.name == "Flight Computer":
            self.update(data_packet[prefix + "e_batt"], 0, data_packet[prefix + "STATE"], False,
                         data_packet[prefix + "timestamp"], data_packet[prefix + "adc_rate"],
                         data_packet[prefix + "telem_rate"])  # no flash state yet, no i_batt
        elif self.name == "Black Box":
            self.update(0, 0, data_packet[prefix + "STATE"], False, data_packet[prefix + "timestamp"],
                         data_packet[prefix + "adc_rate"],
                         data_packet[prefix + "telem_rate"])  # no flash state yet, no i_batt, no e_batt
        elif self.name == "Pressurization Controller":
            self.update(data_packet[prefix + "e_batt"], data_packet[prefix + "i_batt"],
                         data_packet[prefix + "STATE"], data_packet[prefix + "LOGGING_ACTIVE"],
                         data_packet[prefix + "timestamp"],
                         data_packet[prefix + "adc_rate"], data_packet[prefix + "telem_rate"],
                         data_packet[prefix + "state_rem_duration"])
        elif self.name == "GSE Controller":
            self.update(data_packet[prefix + "e_batt"], data_packet[prefix + "ibus"],
                         data_packet[prefix + "STATE"], data_packet[prefix + "LOGGING_ACTIVE"],
                         data_packet[prefix + "timestamp"],
                         data_packet[prefix + "adc_rate"], data_packet[prefix + "telem_rate"],
                         0)  # no flash state yet
        else:
            self.update(data_packet[prefix + "e_batt"], data_packet[prefix + "i_batt"],
                         data_packet[prefix + "STATE"], False, data_packet[prefix + "timestamp"],
                         data_packet[prefix + "adc_rate"], data_packet[prefix + "telem_rate"],
                         0)  # no flash state yet
