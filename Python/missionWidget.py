from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants
from overrides import overrides
from indicatorLightWidget import IndicatorLightWidget

import math
import time

"""
This file contains the class to create the main controls widget (where the P&ID is)
"""


class MissionWidget(QWidget):
    """
    Class that creates the Control Widget. This widget contains all the graphical representations of objects, that can
    also be interacted with
    """

    def __init__(self, parent=None):
        """
        Initialize the widget
        :param parent: parent of this widget, is the central widget
        """
        super().__init__(parent)

        # The usual references
        self.parent = parent
        self.centralWidget = parent
        self.controlsWidget = self.centralWidget.controlsWidget
        self.controlsPanelWidget = self.centralWidget.controlsPanelWidget
        self.window = self.centralWidget.window
        self.gui = self.centralWidget.gui
        self.client = self.window.client_dialog.client

        # Thread
        self.thread = MissionWidgetBackgroundThread(self)
        self.thread.start()

        # Set Geometry
        self.width = self.centralWidget.width - self.controlsPanelWidget.width
        self.mainHeight = 85 * self.gui.pixel_scale_ratio[1]
        self.underBarHeight = 25 * self.gui.pixel_scale_ratio[1]
        self.height = self.mainHeight+self.underBarHeight
        self.left = 0
        self.top = 0
        self.setGeometry(self.left, self.top, self.width, self.height)
        # Buffer to the right of labels for the vertical lines
        self.underBarWBuffer = 3 * self.gui.pixel_scale_ratio[0]
        self.mainBarWBuffer = 10 * self.gui.pixel_scale_ratio[0]

        self.show()

        # Painter controls the drawing of everything on the widget
        self.painter = QPainter()

        # Set background color
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Constants.MASA_Blue_color)
        self.setPalette(p)

        # Create the label that will hold the MET counter
        self.MET_label = QLabel(self)
        MET_font = QFont()
        MET_font.setStyleStrategy(QFont.PreferAntialias)
        MET_font.setFamily(Constants.monospace_font)
        MET_font.setPointSizeF(48 * self.gui.font_scale_ratio)
        self.MET_label.setFont(MET_font)
        self.MET_label.setText("MET-00:00:00")
        self.MET_label.setStyleSheet("color: white")
        self.MET_label.setFixedHeight(self.mainHeight)
        self.MET_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.MET_label.move(0, 0-4*self.gui.pixel_scale_ratio[1])  # Nasty but makes it look more centered
        self.MET_label.show()
        # The right position of the MET label, with a 10 pixel buffer
        self.MET_labelRPos = self.MET_label.width() + self.mainBarWBuffer

        # Connect the MET label to the Run MET update function
        self.gui.run.updateMETSignal.connect(self.updateMETLabel)

        # Light mono space font to use
        monospace_light_font = QFont()
        monospace_light_font.setStyleStrategy(QFont.PreferAntialias)
        monospace_light_font.setFamily(Constants.monospace_font)
        monospace_light_font.setWeight(QFont.Light)

        # Date time label to display the current date and time
        self.dateTimeLabel = QLabel(self)
        monospace_light_font.setPointSizeF(16 * self.gui.font_scale_ratio)
        self.dateTimeLabel.setFont(monospace_light_font)
        self.dateTimeLabel.setStyleSheet("color: white")
        self.dateTimeLabel.setText("November 25th 2020, 05:52pm")
        self.dateTimeLabel.setFixedHeight(self.underBarHeight)
        self.dateTimeLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # self.dateTimeLabel.setStyleSheet("background-color: red")
        self.dateTimeLabel.move(0, self.mainHeight)
        self.updateDateTimeLabel()
        self.dateTimeLabel.show()
        # The right position of the dateTimeLabel, with a  buffer
        self.dateTimeLabelRPos = self.dateTimeLabel.width() + self.underBarWBuffer

        # Title label
        self.titleLabel = QLabel(self)
        monospace_light_font.setPointSizeF(16 * self.gui.font_scale_ratio)
        self.titleLabel.setStyleSheet('QLabel {color: #ffcb05;}') # MASA Maize
        self.titleLabel.setFont(monospace_light_font)
        self.titleLabel.setText("")
        self.titleLabel.setFixedHeight(self.underBarHeight)
        self.titleLabel.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.titleLabel.move(self.dateTimeLabelRPos + self.underBarWBuffer, self.mainHeight)
        self.titleLabel.show()

        # Set all the indicators, move into position
        self.runIndicator = IndicatorLightWidget(self, 'Run', 20, "Red", 14, 20, 5, 2)
        self.runIndicator.setToolTip("Run has not started")
        self.runIndicator.move(self.MET_labelRPos, 0)

        self.connectionIndicator = IndicatorLightWidget(self, 'Connection', 20, "Red", 14, 20, 5, 2)
        self.connectionIndicator.move(self.runIndicator.pos().x() + self.runIndicator.width(), 0)
        self.connectionIndicator.setToolTip("No connection")

        self.commandIndicator = IndicatorLightWidget(self, 'Command', 20, "Red", 14, 20, 5, 2)
        self.commandIndicator.move(self.connectionIndicator.pos().x() + self.connectionIndicator.width(), 0)
        self.commandIndicator.setToolTip("In command")

        self.systemIndicator = IndicatorLightWidget(self, 'System', 20, "Red", 14, 20, 5, 1)
        self.systemIndicator.move(self.commandIndicator.pos().x() + self.commandIndicator.width(), 0)
        self.systemIndicator.setToolTip("He Tank Overpressure\n No pneumatic pressure")

        # self.stateIndicator = IndicatorLightWidget(self, 'State', 20, "Red", 14, 20, 5, 2)
        # self.stateIndicator.move(self.systemIndicator.pos().x() + self.systemIndicator.width(), 0)
        # self.stateIndicator.setToolTip("No state data")

        # Create the label that will hold the status label, displays what task is being performed
        self.status_label = QLabel(self)
        self.status_label.setFont(MET_font)
        self.status_label.setText("GUI Configuration")
        self.status_label.setStyleSheet("color: white")
        self.status_label.setFixedHeight(self.mainHeight)
        self.status_label.setFixedWidth(self.width - (self.systemIndicator.pos().x() + self.systemIndicator.width()))
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_label.move(self.systemIndicator.pos().x() + self.systemIndicator.width() + self.mainBarWBuffer, 0 - 4 * self.gui.pixel_scale_ratio[1])  # Nasty but makes it look more centered
        self.status_label.show()

        # Connect the start of the run to function to allow updating
        self.gui.run.runStartSignal.connect(self.updateWidgetOnRunStart)
        self.gui.run.runEndSignal.connect(self.updateWidgetOnRunEnd)

        self.show()

    def updateMETLabel(self, MET_time):
        """
        This function is called to update the MET label, this function is connected to signal in run class
        :param MET_time: The MET time in milliseconds
        """
        # Convert to Qtime to allow for easier string creation
        qtime = QTime(0, 0, 0)  # Can't pass in directly because the initializer does not like secs above 59
        qtime = qtime.addSecs(math.floor(MET_time/1000.0))

        # Updating Label text
        self.MET_label.setText("MET-" + qtime.toString("hh:mm:ss"))

    def updateStatusLabel(self, status: str, is_warning: bool = False):
        """
        Update the status label
        :param status: new status to display
        :param is_warning: optional argument to pass that will show the status in red instead of the normal white
        """

        self.status_label.setText(status)

        if is_warning:
            self.status_label.setStyleSheet("color:" + Constants.MASA_Maize_color.name())
        else:
            self.status_label.setStyleSheet("color: white")


    def updateDateTimeLabel(self):
        """
        Update the date time label that displays the current date and time for the user, this is called once a second
        from the background thread
        """
        # Get the current date time
        currentDateTime = QDateTime.currentDateTime()

        # Find what day it is and see what suffix it needs
        day = int(currentDateTime.toString('dd'))
        if 11 <= day <= 13:
            dayString = "th "
        elif day % 10 == 1:
            dayString = "st "
        elif day % 10 == 2:
            dayString = "nd "
        elif day % 10 == 3:
            dayString = "rd "
        else:
            dayString = "th "

        # Convert DateTime to string and put it on the label
        dateTimeString = currentDateTime.toString("MMMM dd") + dayString + currentDateTime.toString("yyyy, hh:mmap")
        self.dateTimeLabel.setText(dateTimeString)

    def updateWidgetOnRunStart(self):
        """
        Function that is called when a run is started to populate the widget with updated values
        """
        # Update start time tooltip
        self.MET_label.setToolTip("Start time: " + self.gui.run.startDateTime.time().toString("h:mmap"))
        # Add in title label
        self.titleLabel.setText(self.gui.run.title)
        self.titleLabel.adjustSize()
        # Set run indicator to green
        self.runIndicator.setIndicatorColor("Green")
        self.runIndicator.setToolTip("Run is Active")

        self.update()

    def updateWidgetOnRunEnd(self):
        """
        Function that is called when a run is ended to populate the widget with updated values
        """
        self.runIndicator.setIndicatorColor("Red")
        self.runIndicator.setToolTip("Run has stopped")
         # Add in title label
        self.titleLabel.setText("")
        self.titleLabel.adjustSize()
        self.update()

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
        path.moveTo(0, self.mainHeight-1)  # Bottom left corner
        path.lineTo(self.width, self.mainHeight-1)  # Straight across

        # Draw the vertical line to the right of MET
        path.moveTo(self.MET_labelRPos, self.mainHeight-1)
        path.lineTo(self.MET_labelRPos, 0)

        self.painter.drawPath(path)

        # Border around the date time label
        path = QPainterPath()
        pen.setWidth(Constants.line_width/2)
        self.painter.setPen(pen)
        path.moveTo(0, self.height - 1)
        path.lineTo(self.dateTimeLabel.width() + self.underBarWBuffer, self.height - 1)
        path.lineTo(self.dateTimeLabel.width() + self.underBarWBuffer, self.mainHeight)

        # The outline for the title label, only drawn when the title is not empty
        if not self.titleLabel.text() == "":
            path.moveTo(self.dateTimeLabel.width() + self.underBarWBuffer, self.height-1)
            path.lineTo(self.dateTimeLabelRPos + self.underBarWBuffer + self.titleLabel.width() + self.underBarWBuffer, self.height-1)
            path.lineTo(self.dateTimeLabelRPos + self.underBarWBuffer + self.titleLabel.width() + self.underBarWBuffer, self.mainHeight)

        self.painter.drawPath(path)

        path = QPainterPath()
        pen.setWidth(Constants.line_width)
        self.painter.setPen(pen)
        # Draw the vertical line to the right of indicators
        path.moveTo(self.systemIndicator.pos().x() + self.systemIndicator.width(), self.mainHeight - 1)
        path.lineTo(self.systemIndicator.pos().x() + self.systemIndicator.width(), 0)

        # Draw path and end
        self.painter.drawPath(path)
        self.painter.end()
    
    @overrides
    def update(self):
        super().update()
        # connection

        if self.client.is_connected and self.window.last_packet["actively_rx"]:
            self.connectionIndicator.setIndicatorColor("Green")
            self.connectionIndicator.setToolTip("Server Connected\nSerial Open\nGood Data\nServer Error Message: " + self.window.last_packet["error_msg"])
        elif self.client.is_connected and self.window.last_packet["ser_open"]:
            self.connectionIndicator.setIndicatorColor("Yellow")
            self.connectionIndicator.setToolTip("Server Connected\nSerial Open\nNo Data\nServer Error Message: " + self.window.last_packet["error_msg"])
        elif self.client.is_connected and self.window.last_packet["ser_open"]:
            self.connectionIndicator.setIndicatorColor("Yellow")
            self.connectionIndicator.setToolTip("Server Connected\nSerial Closed\nNo Data")
        else:
            self.connectionIndicator.setIndicatorColor("Red")
            self.connectionIndicator.setToolTip("No Server Connection")
        
        # commander
        if self.client.is_commander:
            self.commandIndicator.setIndicatorColor("Green")
            self.commandIndicator.setToolTip("In Command")
        else:
            self.commandIndicator.setIndicatorColor("Red")
            self.commandIndicator.setToolTip("No Command Authority")


class MissionWidgetBackgroundThread(QThread):
    """
    Class that handles background threading for the mission widget class, this is to prevent the GUI from hanging
    """

    def __init__(self, missionWidget):
        """
        Initializer
        :param missionWidget: The mission Widget
        """
        super().__init__()
        self.missionWidget = missionWidget

    def run(self):
        """
        This is the function that is constantly running in the background
        """

        # While the run is active keep the thread alive, will cleanly exit when run stops
        while True:
            # Update the datetime every second, this can be increased but seems unnecessary
            time.sleep(1)
            self.missionWidget.updateDateTimeLabel()


