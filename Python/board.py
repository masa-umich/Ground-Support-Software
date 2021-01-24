from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from datetime import datetime

from overrides import overrides
from constants import Constants
from customLabel import CustomLabel
from indicatorLightWidget import IndicatorLightWidget


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
        self.painter = QPainter()
        self.client = self.controlsSidebarWidget.window.client_dialog.client

        self.setGeometry(0, 0, self.controlsSidebarWidget.width, 200*self.gui.pixel_scale_ratio[1])

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

        # Connection status indicator light
        self.connectionIndicator = IndicatorLightWidget(self, '', 10, "Red", 10, 10, 10, 1)
        self.connectionIndicator.setToolTip("No connection")
        self.connectionIndicator.move(self.width()-self.connectionIndicator.width(), 0)

        # Board name label
        self.name_label = CustomLabel(self, self.gui, text=self.name)
        self.name_label.setFontSize(16 * self.gui.font_scale_ratio)
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
        self.Ebatt_label = self.createDataFormLayoutLabel("11.1V")

        amp_form_label = self.createDataFormLayoutLabel("ibatt:")
        self.amp_label = self.createDataFormLayoutLabel("2.2a")

        # temp_form_label = self.createDataFormLayoutLabel("Temp:")
        # self.temp_label = self.createDataFormLayoutLabel("--K")

        flash_form_label = self.createDataFormLayoutLabel("Flash:")
        self.flash_label = self.createDataFormLayoutLabel("Inactive")

        LPT_form_label = self.createDataFormLayoutLabel("LP Time:")
        self.LPT_label = self.createDataFormLayoutLabel("247ms")

        adcrate_form_label = self.createDataFormLayoutLabel("ADC Rate:")
        self.adcrate_label = self.createDataFormLayoutLabel("200Hz")

        telemrate_form_label = self.createDataFormLayoutLabel("Tx Rate:")
        self.telemrate_label = self.createDataFormLayoutLabel("10Hz")

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
        font.setPointSize(13 * self.gui.font_scale_ratio)

        if self.gui.platform == "OSX":
            fwidth = self.width()/4 * 1
        else:
            fwidth = self.width()/4 * .85

        # Create the buttons, make sure there is no default option, and connect to functions
        self.manual_button = QPushButton("Manual")
        self.manual_button.setDefault(False)
        self.manual_button.setAutoDefault(False)
        self.manual_button.clicked.connect(lambda: self.sendBoardState("Manual-Disarm"))
        self.manual_button.setFont(font)
        self.manual_button.setFixedWidth(fwidth)

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

        abort_button = QPushButton("Abort")
        abort_button.setDefault(False)
        abort_button.setAutoDefault(False)
        abort_button.clicked.connect(lambda: self.sendBoardState("Abort"))
        abort_button.setFont(font)
        abort_button.setFixedWidth(fwidth)

        # Set text depending on board
        if self.name == "Engine Controller":
            self.fire_button.setText("Hotfire")
        elif self.name == "Pressurization Controller":
            self.fire_button.setText("Press")
        elif self.name == "Flight Computer":
            self.fire_button.setText("Launch")
        else:
            self.fire_button.setText("Order 66")

        buttonLayout.addWidget(self.manual_button)
        buttonLayout.addWidget(self.arm_button)
        buttonLayout.addWidget(self.fire_button)
        buttonLayout.addWidget(abort_button)

        self.show()  # Need to show before able to access some data_frame values
        self.setBoardState(self.state)

        # Set the board height to be the same size as the text because it looks good
        self.board_height = self.telemrate_label.pos().y() + self.telemrate_label.height() + self.data_frame.y() - self.board_pos.y()

        # Update the frame geometry
        self.state_frame.setGeometry(0, self.board_height + self.board_pos.y(), self.width(), self.height()-(state_form_label.height() + self.board_height + self.board_pos.y()))

        # Move to position, little dirty atm
        state_form_label.move(self.board_pos.x(), self.state_frame.y()+self.state_frame.height() + -8 * self.gui.pixel_scale_ratio[1])
        self.state_label.move(state_form_label.x()+state_form_label.width()+3, self.state_frame.y()+self.state_frame.height() + -8 * self.gui.pixel_scale_ratio[1])

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

        # If arm/disarmed command is sent toggle, only toggle if state is manual to arm, otherwise always disarm
        if identifier == "Manual-Disarm":
            newState = 0
        elif identifier == "Arm":
            newState = 1
        # If state is armed, allow for state to be run
        elif identifier == "Run":
            if self.state == 1:
                newState = 2
        # Anytime can call an abort to abort out
        elif identifier == "Abort":
            newState = 3
        else:
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
            self.client.command(3, cmd_dict)

    def setBoardState(self, state: int):
        """
        Sets the current board state, updates all the buttons and state labels
        :param state: state to set
        """

        # Set state
        self.state = state

        # Map of state
        stateMap = {
            -1: "",
            0: "Manual",
            1: "Armed",
            2: "Run",
            3: "Abort"
        }

        # Update labels
        self.state_label.setText(stateMap[self.state])

        if self.state is 1:
            self.manual_button.setText("Disarm")
            self.fire_button.setEnabled(True)
        else:
            self.manual_button.setText("Manual")
            self.fire_button.setEnabled(False)

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
            self.painter.drawEllipse(QPoint(self.board_pos.x() + self.board_width * .25,self.board_pos.y()+ self.board_height/2),2.5*connector_diam, 2.5*connector_diam)
        elif self.name == "Pressurization Controller":
            self.painter.drawEllipse(QPoint(self.board_pos.x() + self.board_width * .15, self.board_pos.y() + self.board_height / 2), 1.5 * connector_diam, 1.5 * connector_diam)
            self.painter.drawEllipse(
                QPoint(self.board_pos.x() + self.board_width * .45, self.board_pos.y() + self.board_height / 2),
                1.5 * connector_diam, 1.5 * connector_diam)
            self.painter.drawEllipse(
                QPoint(self.board_pos.x() + self.board_width * .80, self.board_pos.y() + self.board_height / 2),
                1.5 * connector_diam, 1.5 * connector_diam)
        elif self.name == "Engine Controller" or self.name == "GSE Controller":
            self.painter.drawEllipse(QPoint(self.board_pos.x() + self.board_width * .15, self.board_pos.y() + 2*self.board_height / 7), connector_diam, connector_diam)
            self.painter.drawEllipse(QPoint(self.board_pos.x() + self.board_width * .38, self.board_pos.y() + 2*self.board_height / 7), connector_diam, connector_diam)
            self.painter.drawEllipse(QPoint(self.board_pos.x() + self.board_width * .59, self.board_pos.y() + 2*self.board_height / 7), connector_diam, connector_diam)
            self.painter.drawEllipse(QPoint(self.board_pos.x() + self.board_width * .85, self.board_pos.y() + 2*self.board_height / 7), connector_diam, connector_diam)
            
            self.painter.drawEllipse(QPoint(self.board_pos.x() + self.board_width * .15, self.board_pos.y() + 5*self.board_height / 7), connector_diam, connector_diam)
            self.painter.drawEllipse(QPoint(self.board_pos.x() + self.board_width * .38, self.board_pos.y() + 5*self.board_height / 7), connector_diam, connector_diam)
            self.painter.drawEllipse(QPoint(self.board_pos.x() + self.board_width * .59, self.board_pos.y() + 5*self.board_height / 7), connector_diam, connector_diam)
            self.painter.drawEllipse(QPoint(self.board_pos.x() + self.board_width * .85, self.board_pos.y() + 5*self.board_height / 7), connector_diam, connector_diam)

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
    def update(self, ebatt, ibatt, state, flash, LPT, adc_rate, telem_rate):
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
        super().update()
        self.Ebatt_label.setText(str(ebatt) + " V")
        self.amp_label.setText(str(ibatt) + " A")
        self.setBoardState(int(state))
        self.flash_label.setText(str(flash))  # todo: flash state parsing
        self.LPT_label.setText(str(LPT))
        self.adcrate_label.setText(str(adc_rate) + " Hz")
        self.telemrate_label.setText(str(telem_rate) + " Hz")
