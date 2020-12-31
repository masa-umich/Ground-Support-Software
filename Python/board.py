from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

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

        self.setGeometry(0, 0, self.controlsSidebarWidget.width, 150*self.gui.pixel_scale_ratio[1])

        # Set background color to match
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Constants.MASA_Blue_color)
        self.setPalette(p)

        # Define geometric of board
        self.board_pos = QPointF(10*self.gui.pixel_scale_ratio[0], 38*self.gui.pixel_scale_ratio[1])
        self.board_width = 150 * self.gui.pixel_scale_ratio[0]
        self.board_height = 80 * self.gui.pixel_scale_ratio[1]

        # Temp holder values
        self.name = name
        self.EBatt = 0
        self.amps = 0
        self.state = "Manual Control"
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
        self.name_label.setFixedHeight(self.connectionIndicator.circle_radius*2)
        self.name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.name_label.move(self.board_pos.x(), self.connectionIndicator.pos().y()+self.connectionIndicator.hBuffer)

        # Set up the data name label
        self.data_frame = QFrame(self)
        self.data_form_layout = QFormLayout(self)
        self.data_frame.resize(self.width() - (self.board_pos.x() + self.board_width)+10*self.gui.pixel_scale_ratio[0],
                                self.height() - (self.name_label.pos().y() + self.name_label.height()))
        self.data_frame.setLayout(self.data_form_layout)
        self.data_frame.move((self.board_pos.x() + self.board_width)-10*self.gui.pixel_scale_ratio[0],
                             (self.name_label.pos().y() + self.name_label.height())-8*self.gui.pixel_scale_ratio[1])

        # Create the labels for the data form
        self.data_form_layout.setLabelAlignment(Qt.AlignLeft)
        EBatt_form_label = self.createDataFormLayoutLabel("EBatt:")
        self.Ebatt_label = self.createDataFormLayoutLabel("11.1V")

        amp_form_label = self.createDataFormLayoutLabel("Amps:")
        self.amp_label = self.createDataFormLayoutLabel("2.2a")

        # temp_form_label = self.createDataFormLayoutLabel("Temp:")
        # self.temp_label = self.createDataFormLayoutLabel("--K")

        flash_form_label = self.createDataFormLayoutLabel("Flash:")
        self.flash_label = self.createDataFormLayoutLabel("Active")

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

        # State label to go below board
        state_form_label = self.createDataFormLayoutLabel("State:")
        self.state_label = self.createDataFormLayoutLabel(self.state)

        # lame lame to set parent
        state_form_label.setParent(self)
        self.state_label.setParent(self)
        state_form_label.adjustSize()
        # Move to position
        state_form_label.move(self.board_pos.x(), self.board_pos.y()+self.board_height + 8 * self.gui.pixel_scale_ratio[1])
        self.state_label.move(state_form_label.x()+state_form_label.width()+3, self.board_pos.y()+self.board_height + 8 * self.gui.pixel_scale_ratio[1])

        self.show()

    @staticmethod
    def createDataFormLayoutLabel(text: str):
        """
        Quick helper method that creates the labels used for the data of this widget
        :param text: label text
        :return: the label that is created
        """
        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.default_font)

        label = QLabel(text)
        label.setFixedHeight(14)
        label.setFont(font)

        return label

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