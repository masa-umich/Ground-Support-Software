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
        #self.client = self.window.client_dialog #.client

        # Thread
        self.thread = MissionWidgetBackgroundThread(self)
        self.thread.start()

        self.thread.updateStatusIndicatorSignal.connect(self.updateSystemStatus)

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

        self.gui.liveDataHandler.connectionStatusSignal.connect(self.updateConnectionStatus)
        # TODO: Currently one of these in the controlsWidget class so maybe combine
        self.gui.liveDataHandler.updateScreenSignal.connect(self.update)

        self.show()

        # Painter controls the drawing of everything on the widget
        self.painter = QPainter()

        # Set background color
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Constants.MASA_Blue_color)
        self.setPalette(p)

        # Create the label that will hold the CET counter
        self.CET_label = CustomCETLabel(self)
        CET_font = QFont()
        CET_font.setStyleStrategy(QFont.PreferAntialias)
        CET_font.setFamily(Constants.monospace_font)
        CET_font.setPointSizeF(48 * self.gui.font_scale_ratio)
        CET_font.setHintingPreference(QFont.PreferNoHinting)
        self.CET_label.setFont(CET_font)

        self.CET_static_tooltip = ""  # Random var to track ending portion of tooltip. More below

        CET_tooltip_font = QFont()
        CET_tooltip_font.setStyleStrategy(QFont.PreferAntialias)
        CET_tooltip_font.setFamily(Constants.monospace_font)
        CET_tooltip_font.setPointSizeF(12 * self.gui.font_scale_ratio)
        CET_tooltip_font.setHintingPreference(QFont.PreferNoHinting)
        QToolTip.setFont(CET_tooltip_font)

        self.CET_label.setText("CET-00:00:00")
        self.CET_label.setStyleSheet("color: white")
        self.CET_label.setFixedHeight(self.mainHeight)
        self.CET_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.CET_label.move(0, 0-4*self.gui.pixel_scale_ratio[1])  # Nasty but makes it look more centered
        self.CET_label.show()
        # The right position of the CET label, with a 10 pixel buffer
        self.CET_labelRPos = self.CET_label.width() + self.mainBarWBuffer

        # Connect the CET label to the Run CET update function
        self.gui.campaign.updateCETSignal.connect(self.updateCETLabel)

        # Light mono space font to use
        monospace_light_font = QFont()
        monospace_light_font.setStyleStrategy(QFont.PreferAntialias)
        monospace_light_font.setFamily(Constants.monospace_font)
        monospace_light_font.setWeight(QFont.Light)

        # Date time label to display the current date and time
        self.dateTimeLabel = QLabel(self)
        monospace_light_font.setPointSizeF(16 * self.gui.font_scale_ratio)
        monospace_light_font.setHintingPreference(QFont.PreferNoHinting)
        self.dateTimeLabel.setFont(monospace_light_font)
        self.dateTimeLabel.setStyleSheet("color: white")
        self.dateTimeLabel.setText("November 25th 2020, 05:52pm")
        self.dateTimeLabel.setFixedHeight(self.underBarHeight)
        self.dateTimeLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # self.dateTimeLabel.setStyleSheet("background-color: red")
        self.dateTimeLabel.move(0, self.mainHeight-1)
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
        self.titleLabel.move(self.dateTimeLabelRPos + self.underBarWBuffer, self.mainHeight-1)
        self.titleLabel.show()

        # Set all the indicators, move into position
        self.campaignIndicator = IndicatorLightWidget(self, 'Campaign', 20, "Red", 14, 30, 5, 2)
        self.campaignIndicator.setToolTip("Campaign has not started")
        self.campaignIndicator.move(self.CET_labelRPos, 0)

        self.connectionIndicator = IndicatorLightWidget(self, 'Connection', 20, "Red", 14, 30, 5, 2)
        self.connectionIndicator.move(self.campaignIndicator.pos().x() + self.campaignIndicator.width(), 0)
        self.connectionIndicator.setToolTip("No connection")

        self.commandIndicator = IndicatorLightWidget(self, 'Command', 20, "Red", 14, 30, 5, 2)
        self.commandIndicator.move(self.connectionIndicator.pos().x() + self.connectionIndicator.width(), 0)
        self.commandIndicator.setToolTip("In command")

        self.systemIndicator = IndicatorLightWidget(self, 'System', 20, "Green", 14, 30, 5, 1)
        self.systemIndicator.move(self.commandIndicator.pos().x() + self.commandIndicator.width(), 0)
        self.systemIndicator.setToolTip("Norminal")

        # self.stateIndicator = IndicatorLightWidget(self, 'State', 20, "Red", 14, 20, 5, 2)
        # self.stateIndicator.move(self.systemIndicator.pos().x() + self.systemIndicator.width(), 0)
        # self.stateIndicator.setToolTip("No state data")

        # Create the label that will hold the status label, displays what task is being performed
        self.status_label = QLabel(self)
        self.status_label.setFont(CET_font)
        self.status_label.setText("GUI Configuration")
        self.status_label.setStyleSheet("color: white")
        self.status_label.setFixedHeight(self.mainHeight)
        self.status_label.setFixedWidth(self.width - (self.systemIndicator.pos().x() + self.systemIndicator.width()))
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_label.move(self.systemIndicator.pos().x() + self.systemIndicator.width() + self.mainBarWBuffer, 0 - 4 * self.gui.pixel_scale_ratio[1])  # Nasty but makes it look more centered
        self.status_label.show()

        # Connect the start of the run to function to allow updating
        self.gui.campaign.campaignStartSignal.connect(self.updateWidgetOnCampaignStart)
        self.gui.campaign.campaignEndSignal.connect(self.updateWidgetOnCampaignEnd)
        self.gui.campaign.testStartSignal.connect(self.updateWidgetOnTestStart)
        self.gui.campaign.testEndSignal.connect(self.updateWidgetOnTestEnd)

        self.show()

    # TODO: Move this to campaign class
    @staticmethod
    def generateCETAsText(CET_time, test_start_time: int = None):
        """
        This function generates a string from the CET time
        :param CET_time: CET in milliseconds
        :param test_start_time: option time that test started, will then return TET instead of CET. See below
        updateCETLabel for more
        :return: string as time
        """
        # Convert to Qtime to allow for easier string creation
        qtime = QTime(0, 0, 0)  # Can't pass in directly because the initializer does not like secs above 59
        if test_start_time is not None:
            qtime = qtime.addSecs(math.floor((CET_time-test_start_time) / 1000.0))
            return "TET-" + qtime.toString("hh:mm:ss")
        else:
            qtime = qtime.addSecs(math.floor(CET_time / 1000.0))
            return "CET-" + qtime.toString("hh:mm:ss")

    def updateCETLabel(self, CET_time, test_start_time: int):
        """
        This function is called to update the CET label, this function is connected to signal in run class. In the case
        that a test is currently active, we want this to show the test time, not the CET
        :param CET_time: The CET time in milliseconds
        :param test_start_time: option time that test started
        """
        # Updating Label text
        self.CET_label.setText(self.generateCETAsText(CET_time, test_start_time))

        if self.gui.campaign.isTestActive:
            self.CET_label.setToolTip("Current " + self.generateCETAsText(self.gui.campaign.CET) + "\n" + self.CET_static_tooltip)
            self.CET_label.liveUpdateText()
        else:
            self.CET_label.setToolTip(self.CET_static_tooltip)
            self.CET_label.liveUpdateText()

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

    @pyqtSlot(str)
    def updateWidgetOnTestStart(self, test_name: str):
        self.titleLabel.setText(self.gui.campaign.title + ': ' + test_name)
        self.titleLabel.adjustSize()
        self.campaignIndicator.setToolTip("Campaign is Active\nTest is Active")
        self.CET_static_tooltip = self.CET_label.toolTip() + "\n" + f'{"Test: " + test_name:<31} {"start: "+ QDateTime.currentDateTime().time().toString("h:mmap") + " ("+self.generateCETAsText(self.gui.campaign.CET) + ")":<26}'
        self.CET_label.setToolTip("Current " + self.generateCETAsText(self.gui.campaign.CET) + "\n" + self.CET_static_tooltip)
        self.update()

    @pyqtSlot()
    def updateWidgetOnTestEnd(self):
        self.titleLabel.setText(self.gui.campaign.title)
        self.titleLabel.adjustSize()
        self.campaignIndicator.setToolTip("Campaign is Active")
        self.CET_static_tooltip = self.CET_label.toolTip() + f'{"   |   end: "+ QDateTime.currentDateTime().time().toString("h:mmap") + " ("+self.generateCETAsText(self.gui.campaign.CET) + ")":<26}'
        self.CET_label.setToolTip("Current " + self.generateCETAsText(self.gui.campaign.CET) + "\n" + self.CET_static_tooltip)

        self.update()

    def updateWidgetOnCampaignStart(self):
        """
        Function that is called when a run is started to populate the widget with updated values
        """
        # Update start time tooltip
        self.CET_label.setToolTip("Campaign start: " + self.gui.campaign.startDateTime.time().toString("h:mmap") + " (CET-00:00:00)\n")
        self.CET_static_tooltip = "Campaign start: " + self.gui.campaign.startDateTime.time().toString("h:mmap") + " (CET-00:00:00)\n"
        # Add in title label
        self.titleLabel.setText(self.gui.campaign.title)
        self.titleLabel.adjustSize()
        # Set run indicator to green
        self.campaignIndicator.setIndicatorColor("Green")
        self.campaignIndicator.setToolTip("Campaign is Active")

        self.update()

    def updateWidgetOnCampaignEnd(self):
        """
        Function that is called when a run is ended to populate the widget with updated values
        """
        self.campaignIndicator.setIndicatorColor("Red")
        self.campaignIndicator.setToolTip("Campaign has stopped")
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

        # Draw the vertical line to the right of CET
        path.moveTo(self.CET_labelRPos, self.mainHeight-1)
        path.lineTo(self.CET_labelRPos, 0)

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

    @pyqtSlot(int, str, bool)
    def updateConnectionStatus(self, status: int, error_string: str, is_commander: bool):
        # All is well
        if status == 0:
            self.connectionIndicator.setIndicatorColor("Green")
            self.connectionIndicator.setToolTip(
                "Server Connected\nSerial Open\nGood Data\nServer Error Message: " + error_string)
        # Server to GUI connection is good, but data should be coming from board, but it is bad or is delayed
        elif status == 1:
            self.connectionIndicator.setIndicatorColor("Yellow")
            self.connectionIndicator.setToolTip(
                "Server Connected\nSerial Open\nNo Data\nServer Error Message: " + error_string)
        # Server to GUI connection is good, but there is no open serial (no way for pacets to be recieved)
        elif status == 2:
            self.connectionIndicator.setIndicatorColor("Yellow")
            self.connectionIndicator.setToolTip("Server Connected\nSerial Closed\nNo Data\nServer Error Message: " + error_string)
        # Server to GUI connection bad, no info to display at the time
        elif status == 3:
            self.connectionIndicator.setIndicatorColor("Red")
            self.connectionIndicator.setToolTip("No Server Connection")

        # commander
        if is_commander:
            self.commandIndicator.setIndicatorColor("Green")
            self.commandIndicator.setToolTip("In Command")
        else:
            self.commandIndicator.setIndicatorColor("Red")
            self.commandIndicator.setToolTip("No Command Authority")

    @pyqtSlot(int, str)
    def updateSystemStatus(self, status, tooltip):

        if status == 0:
            self.systemIndicator.setIndicatorColor("Green")
        elif status == 1:
            self.systemIndicator.setIndicatorColor("Yellow")
        elif status == 2:
            self.systemIndicator.setIndicatorColor("Red")

        self.systemIndicator.setToolTip(tooltip)


class MissionWidgetBackgroundThread(QThread):
    """
    Class that handles background threading for the mission widget class, this is to prevent the GUI from hanging
    """

    updateStatusIndicatorSignal = pyqtSignal(int, str)

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
            # Now 0.2, to make the status update seem more instant
            time.sleep(0.2)
            self.missionWidget.updateDateTimeLabel()

            # All this junk below is updating the system indicator light, may need to move again in the future
            object_status_tooltip = {0: ":)", 1: "", 2: ""}
            general_status_tooltip = {0: "", 1: "", 2: ""}
            max_status = 0

            if len(self.missionWidget.centralWidget.controlsSidebarWidget.board_objects) == 0:
                general_status_tooltip[1] = "No avionics boards added (Edit->Add Avionics)\n"
                max_status = max(1, max_status)

            for object_ in self.missionWidget.controlsWidget.object_list:
                status, message = object_.objectStatusCheck()

                if status > 0:
                    max_status = max(max_status, status)
                    object_status_tooltip[status] = object_status_tooltip[status] + message + "\n"

            # Nasty block, first checks to see if there are both critical and warnings or just one or the other.
            # Then actually sets the tooltip in right format to display
            if (len(general_status_tooltip[1]) > 0 or len(object_status_tooltip[1])) > 0 and (len(general_status_tooltip[2]) > 0 or len(object_status_tooltip[2]) > 0):
                tooltip = "Critical: \n" + general_status_tooltip[2] + object_status_tooltip[2] + "\nWarnings: \n" + general_status_tooltip[1] + object_status_tooltip[1]
            elif len(general_status_tooltip[1]) > 0 or len(object_status_tooltip[1]) > 0:
                tooltip = "Warnings: \n" + general_status_tooltip[1] + object_status_tooltip[1]
            elif len(general_status_tooltip[2]) > 0 or len(object_status_tooltip[2]) > 0:
                tooltip = "Critical: \n" + general_status_tooltip[2] + object_status_tooltip[2]
            else:
                tooltip = object_status_tooltip[0]

            tooltip = tooltip.rstrip('\r\n')
            self.updateStatusIndicatorSignal.emit(max_status, tooltip)

            if self.missionWidget.gui.campaign.is_active:
                self.missionWidget.gui.campaign.updateCET()


class CustomCETLabel(QLabel):

    def __init__(self, widget_parent):
        super().__init__(widget_parent)
        self._last_event_pos = None

    @overrides
    def event(self, e: QEvent):
        """
        Grabs the tooltip event and saves the position down.
        :param e: event
        :return: whatever the super specifies, need to do this so all events are still handled
        """
        if e.type() == QEvent.ToolTip:
            self._last_event_pos = e.globalPos()
            QToolTip.showText(self._last_event_pos, self.toolTip())
        elif e.type() == QEvent.Leave:
            self._last_event_pos = None

        return super().event(e)

    def liveUpdateText(self):
        """
        Simply hides tooltip text and then re-shows it to allow the tooltip to update as you hover
        """
        if self._last_event_pos is not None:
            #QToolTip.hideText()
            QToolTip.showText(self._last_event_pos, self.toolTip())




