from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys
import time
from PyQt5 import QtGui, QtCore, QtWidgets

from controlsWidget import ControlsWidget
from controlsPanelWidget import ControlsPanelWidget
from controlsSidebarWidget import ControlsSidebarWidget
from missionWidget import MissionWidget
from constants import Constants
from ClientWidget import ClientWidget, ClientDialog
from data_viewer import DataViewerDialog
from s2Interface import S2_Interface
from flash import FlashWindow
from abort_button import AbortButton
from limits import LimitWindow
from auto_manager import AutoManager
from dp import TankLevelDialog
from sensor_calibrations import SensorCalibrationDialog

from overrides import overrides
import os
import ctypes
import webbrowser
from datetime import datetime

"""
This file contains the class to create the main window
"""


class ControlsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        # Set geometry
        self.gui = parent
        self.title = 'MASA Console'
        self.setWindowIcon(QIcon('Images/M_icon.png'))
        #self.client = ClientWidget(True, self)  # control client
        self.last_packet = {}
        self.interface = S2_Interface()
        self.statusBar().setFixedHeight(22 * self.gui.pixel_scale_ratio[1])
        self.button_box = AbortButton(self.gui)  # .client)
        self.limits = LimitWindow(10, gui=self.gui)  # .client)
        self.auto_manager = AutoManager(self.gui) #.client)
        self.tank_levels = TankLevelDialog(dual=False, gui = self.gui)
        self.sensorsWindow = SensorCalibrationDialog(self.gui)
        self.data_viewer_dialog = DataViewerDialog(self.gui)
        self.menuBar().setFixedHeight(32 * self.gui.pixel_scale_ratio[1])
        if self.gui.platform == "Windows":
            # Need to pull out the title bar height, and menu bar height from windows
            # TODO: Move the title bar height adjustment to screen resolution
            self.setGeometry(0, 0, self.gui.screenResolution[0], self.gui.screenResolution[1]-QApplication.style().pixelMetric(QStyle.PM_TitleBarHeight) - self.menuBar().height())
        else:
            self.setGeometry(0, 0, self.gui.screenResolution[0], self.gui.screenResolution[1] - self.statusBar().height())

        self.centralWidget = ControlsCentralWidget(self, self)
        self.setCentralWidget(self.centralWidget)
        self.fileName = ""
        self.setWindowTitle(self.title)
        self.flash_dialog = FlashWindow(self.gui)
        self.gui.liveDataHandler.connectionStatusSignal.connect(self.updateFromConnectionStatus)

        appid = 'MASA.GUI' # arbitrary string
        if os.name == 'nt': # Bypass command because it is not supported on Linux 
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
        else:
            pass

        # Setup Status bar
        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.monospace_font)
        font.setPointSizeF(14 * self.gui.font_scale_ratio)
        self.statusBar().setFont(font)

        # Menu system, probably should be its own function, allows things to be placed in menu bar at top of application
        exitAct = QAction('&Save and Quit', self)
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.gui.guiExit)

        # The next several segments of code create objects to represent each button action for the toolbar
        # Each segment has a comment above it describing what action it implements
        # The third line of each segment calls a function, defined below, that carries out the action of the button
        # Help menu is added in the baseGUI class
        # FILE -> New
        newAct = QAction('&New Configuration', self)
        newAct.setShortcut('Ctrl+N')
        newAct.triggered.connect(self.newFile)

        # FILE -> Open
        openAct = QAction('&Open Configuration', self)
        openAct.setShortcut('Ctrl+O')
        openAct.triggered.connect(self.openFileDialog)

        # FILE -> Save
        saveAct = QAction('&Save Configuration', self)
        saveAct.setShortcut('Ctrl+S')
        saveAct.triggered.connect(self.saveRegular)

        # FILE -> Save As
        saveAsAct = QAction('&Save Configuration As', self)
        saveAsAct.setShortcut('Ctrl+Shift+S')
        saveAsAct.triggered.connect(self.saveFileDialog)

        # FILE -> Enter Debug Mode
        self.debugAct = QAction('&Enter Debug Mode', self)
        self.debugAct.setShortcut('Ctrl+D')
        self.debugAct.triggered.connect(self.enterDebug)

        # FILE -> Exit Debug Mode
        self.exitDebugAct = QAction('&Leave Debug Mode', self)
        self.exitDebugAct.setShortcut('Ctrl+Shift+D')
        self.exitDebugAct.triggered.connect(self.exitDebug)
        self.exitDebugAct.setDisabled(True)

        # FILE -> Screen Draw Settings
        self.screenSettingsAct = QAction('&Screen Draw Settings', self)
        self.screenSettingsAct.triggered.connect(self.showDrawingSettingsDialog)

        # EDIT -> Enter Edit Mode
        self.enterEditAct = QAction('&Enter Edit Mode', self)
        self.enterEditAct.setShortcut('Ctrl+E')
        self.enterEditAct.triggered.connect(self.enterEdit)

        # EDIT -> Leave Edit Mode
        self.exitEditAct = QAction('&Leave Edit Mode', self)
        self.exitEditAct.setShortcut('Ctrl+Shift+E')
        self.exitEditAct.triggered.connect(self.exitEdit)
        self.exitEditAct.setDisabled(True)  # Start with it disabled

        # EDIT -> Add Boards
        self.addAvionicsAct = QAction('&Add Avionics', self)
        self.addAvionicsAct.triggered.connect(self.showAvionicsDialog)
        self.addAvionicsAct.setShortcut('Alt+A')

        # VIEW -> Show Avionics Mappings
        self.showAvionicsMapAct = QAction('&Show Avionics Mappings', self)
        self.showAvionicsMapAct.triggered.connect(self.centralWidget.controlsWidget.showSensorMappings)

        # VIEW -> Data Viewer
        data_view_dialog = QAction("&Data Viewer", self)
        data_view_dialog.triggered.connect(lambda: self.gui.show_window(self.data_viewer_dialog))

        # VIEW -> Limits
        self.limit_action = QAction('&Limits', self)
        self.limit_action.triggered.connect(lambda: self.gui.show_window(self.limits))
        self.limit_action.setShortcut('Alt+L')

        # VIEW -> Autosequence Manager
        self.auto_action = QAction('Auto&sequence Manager', self)
        self.auto_action.triggered.connect(lambda: self.gui.show_window(self.auto_manager))
        self.auto_action.setShortcut('Alt+S')

        # VIEW -> Level Sensing
        self.level_action = QAction("&Level Sensing", self)
        self.level_action.triggered.connect(lambda: self.gui.show_window(self.tank_levels))
        # self.level_action.setShortcut('Alt+D')

        # Campaign -> Start Campaign
        self.startRunAct = QAction('&Start Campaign', self)
        self.startRunAct.setShortcut('Ctrl+R')
        self.startRunAct.triggered.connect(lambda: self.showRunDialog(False))

        # Campaign -> End Campaign
        self.endRunAct = QAction('&End Campaign', self)
        self.endRunAct.setShortcut('Ctrl+Shift+R')
        self.endRunAct.triggered.connect(self.endRun)
        self.endRunAct.setDisabled(True)  # Start with it disabled

        # Campaign -> Start Test
        self.startTestAct = QAction('&Start Test', self)
        self.startTestAct.setShortcut('Ctrl+T')
        self.startTestAct.triggered.connect(lambda: self.showRunDialog(True))
        self.startTestAct.setDisabled(True)

        # Campaign -> End Test
        self.endTestAct = QAction('&End Test', self)
        self.endTestAct.setShortcut('Ctrl+Shift+T')
        self.endTestAct.triggered.connect(self.endTest)
        self.endTestAct.setDisabled(True)  # Start with it disabled

        # Campaign -> Ambientize
        self.ambientizeMenu = QMenu('Ambientize', self)
        self.ambientizeMenu.triggered.connect(self.ambientizeCmd)
        for board in Constants.boards:
            self.ambientizeMenu.addAction(board)

        # Campaign -> Tare Load Cells
        self.tareLoadCellAct = QAction('Tare GSE Load Cells', self)
        self.tareLoadCellAct.triggered.connect(self.tareLoadCell)

        # Campaign -> Zero Board System Time
        self.zeroTimeAct = QAction('Zero Board System Clocks', self)
        self.zeroTimeAct.triggered.connect(self.zeroSystemClock)

        # Campaign -> Open Campaign Folder
        self.openCampaignDir = QAction('Open Campaign Folder', self)
        self.openCampaignDir.triggered.connect(self.openCampaignFolder)

        # Avionics -> Connection Settings
        self.connect = QAction("&Connection", self)
        self.connect.triggered.connect(lambda: self.gui.show_window(self.gui.liveDataHandler.getClient()))
        self.connect.setShortcut('Alt+C')

        # Avionics -> Flash
        self.flashsettings = QAction("&Flash", self)
        self.flashsettings.triggered.connect(lambda: self.gui.show_window(self.flash_dialog))
        self.flashsettings.setShortcut('Alt+F')

        # Avionics -> Abort Button Settings
        self.buttonBoxAct = QAction('Abort &Button', self)
        self.buttonBoxAct.setShortcut('Alt+B')
        self.buttonBoxAct.triggered.connect(lambda: self.gui.show_window(self.button_box))

        # Avionics -> Sensor Calibrations
        self.sensor_calibration = QMenu("Sensor Calibrations", self)
        self.sensor_calibration.triggered.connect(self.sensorsWindow.calibrateSensorsWindow)
        for board in Constants.boards:
            self.sensor_calibration.addAction(board)

        # Creates menu bar, adds tabs file, edit, view
        menuBar = self.menuBar()
        menuBar.setNativeMenuBar(True)
        menuBar.installEventFilter(self)  # See event filter below, allows for custom event to prevent status bar update
        menuBar.setStyleSheet("background-color:white;border:0;color:black;")
        file_menu = menuBar.addMenu('File')
        edit_menu = menuBar.addMenu('Edit')
        view_menu = menuBar.addMenu('View')
        campaign_menu = menuBar.addMenu('Campaign')

        # Mac does not allow adding buttons directly to menu bar so we will toss them in the avionics group
        # However if the menu bar is not native for whatever reason then can default to windows behavior
        if self.gui.platform == "OSX" and menuBar.isNativeMenuBar():
            avionics_menu = menuBar.addMenu('Avionics')

        # Adds all the file buttons to the file tab
        file_menu.addAction(newAct)
        file_menu.addAction(openAct)
        file_menu.addAction(saveAct)
        file_menu.addAction(saveAsAct)
        file_menu.addAction(exitAct)
        file_menu.addSeparator()
        file_menu.addAction(self.debugAct)
        file_menu.addAction(self.exitDebugAct)
        file_menu.addSeparator()
        file_menu.addAction(self.screenSettingsAct)

        # Adds all the edit button to the edit tab
        edit_menu.addAction(self.enterEditAct)
        edit_menu.addAction(self.exitEditAct)
        edit_menu.addAction(self.addAvionicsAct)

        # Adds all the related view items to view menus
        view_menu.addAction(self.showAvionicsMapAct)
        view_menu.addAction(data_view_dialog)
        view_menu.addAction(self.limit_action)
        view_menu.addAction(self.auto_action)
        view_menu.addAction(self.level_action)

        # Adds any related run buttons to the run tab
        campaign_menu.addAction(self.startRunAct)
        campaign_menu.addAction(self.endRunAct)
        campaign_menu.addSeparator()
        campaign_menu.addAction(self.startTestAct)
        campaign_menu.addAction(self.endTestAct)
        campaign_menu.addSeparator()
        campaign_menu.addMenu(self.ambientizeMenu)
        campaign_menu.addAction(self.tareLoadCellAct)
        campaign_menu.addAction(self.zeroTimeAct)
        campaign_menu.addSeparator()
        campaign_menu.addAction(self.openCampaignDir)

        # If the gui is being run on windows, dont use the menu bar
        if self.gui.platform == "Windows" or (self.gui.platform == "OSX" and not menuBar.isNativeMenuBar()):
            menuBar.addAction(self.connect)
            menuBar.addAction(self.flashsettings)
            menuBar.addAction(self.buttonBoxAct)
            menuBar.addMenu(self.sensor_calibration)

        elif self.gui.platform == "OSX":
            avionics_menu.addAction(self.connect)
            avionics_menu.addAction(self.flashsettings)
            avionics_menu.addAction(self.buttonBoxAct)
            avionics_menu.addMenu(self.sensor_calibration)

        # Add all menus to a dict for easy access by other functions
        # Help menu is added in the baseGUI class
        self.menus = {"File": file_menu,
                      "Edit": edit_menu,
                      "View": view_menu,
                      "Run":  campaign_menu}

        self.showMaximized()

        # Can't assign here see below for more info
        self.central_widget_offset = None

    def postInit(self):
        # So the window does not move to its final position till after exec_ is called on the gui, which means it cannot
        # go in the init_ function. This seems very strange but this appears to be the best solution

        # Not sure why this is different, but seems to due with the fact that windows handles central widget differently
        if self.gui.platform == "Windows":
            self.central_widget_offset = self.centralWidget.pos() - self.pos() + QPointF(0, self.menuBar().height())
        elif self.gui.platform == "OSX":
            self.central_widget_offset = self.pos()

    @overrides
    def eventFilter(self, source, event: QEvent):
        """
        Need an event filter to prevent the menu bar from causing the status bar to disappear
        :param source: the self.blahh of whatever is sending the signal
        :param event: the event triggered
        :return: True for preventing the event to handled again later downstream
        """
        if isinstance(source, QMenuBar) and event.type() == QEvent.StatusTip:
            return True  # Returning true will prevent this event from being processed again down the line

        return super().eventFilter(source, event)

    def saveRegular(self):
        """
        Executes the save action. If file is named, just runs saveData.
        If file is not yet named, executes Save As action.
        """
        if self.fileName != "":
            self.centralWidget.controlsWidget.saveData(self.fileName)
            #self.saveNotes(self.fileName.removesuffix('.json'))
        else:
            self.saveFileDialog()
            #self.saveNotes()

    def saveFileDialog(self):
        """
        Pulls up Save As dialog, saves data to designated file and sets filename field
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, 'Save Configuration', self.gui.workspace_path+"/Configurations", "JSON Files (*.json)", options=options)
        if fileName:
            if fileName.find(".json") == -1:
                fileName = fileName + ".json"
            self.fileName = fileName
            self.centralWidget.controlsWidget.saveData(fileName)

            #self.saveNotes(fileName.removesuffix('.json'))

    def openFileDialog(self):
        """
        Pulls up open file dialog, loads data from selected file
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Configuration", self.gui.workspace_path+"/Configurations", "JSON Files (*.json)", options=options)

        if fileName:
            self.newFile()
            #self.gui.configuration.setFilename(fileName)
            self.fileName = fileName
            self.centralWidget.controlsWidget.loadData(fileName)

            # with open(fileName.removesuffix('.json') + '.txt', "r") as read_file:
            #     data = read_file.read()

            # TODO: Properly remove this/ move somehwere
            # rewrites the notes in the notebox
            #self.centralWidget.controlsSidebarWidget.noteBox.setText(data)

    def newFile(self):
        """
        Creates new blank untitled file. Basically just erases everything and sets filename to unset
        """
        self.fileName = ""
        self.centralWidget.controlsPanelWidget.removeAllEditingObjects()
        self.centralWidget.controlsWidget.last_object_id = 0
        self.centralWidget.controlsWidget.last_tube_id = 0

        for obj in self.centralWidget.controlsWidget.object_type_list:
            self.centralWidget.controlsWidget.object_count[obj.object_name] = 0

        length = len(self.centralWidget.controlsWidget.object_list)
        for i in range(length):
            self.centralWidget.controlsWidget.deleteObject(self.centralWidget.controlsWidget.object_list[0])

        for tube in self.centralWidget.controlsWidget.tube_list:
            tube.deleteTube()

        for board in self.centralWidget.controlsSidebarWidget.board_objects:
            board.deleteLater()
            board = None
            del board

        self.centralWidget.controlsSidebarWidget.board_objects.clear()

        self.gui.setStatusBarMessage("New configuration started")

    def enterEdit(self):
        """
        If not already editing, calls toggle edit to enter edit mode
        """
        if not self.centralWidget.is_editing:
            self.centralWidget.controlsPanelWidget.show()
            self.centralWidget.controlsSidebarWidget.hide()
            self.centralWidget.controlsWidget.toggleEdit()
            self.enterEditAct.setDisabled(True)
            self.exitEditAct.setEnabled(True)
            self.debugAct.setDisabled(True)
            self.exitDebugAct.setDisabled(True)
            self.startRunAct.setDisabled(True)
            self.centralWidget.missionWidget.updateStatusLabel("Edit Mode", True)
            self.gui.setStatusBarMessage("Enter Edit Mode")

    def exitEdit(self):
        """
        Same as enter edit mode, but the opposite
        """
        if self.centralWidget.is_editing:
            self.gui.setStatusBarMessage("Exit Edit Mode")  # Do this up top because we want save to show up if it happens
            self.centralWidget.controlsWidget.toggleEdit()
            self.centralWidget.controlsPanelWidget.hide()
            self.centralWidget.controlsSidebarWidget.show()

            # I tried for about two hours to avoid this, but cant seem to get around that fact that if you add
            # boards while in edit more, they don't show up properly after leaving
            # TODO: Make this not terrible
            board_names = []
            for board in self.centralWidget.controlsSidebarWidget.board_objects:
                board_names.append(board.name)

            self.centralWidget.controlsSidebarWidget.addBoardsToScrollWidget(
                board_names, True)

            self.enterEditAct.setEnabled(True)
            self.exitEditAct.setDisabled(True)
            self.debugAct.setEnabled(True)
            self.exitDebugAct.setEnabled(True)
            self.startRunAct.setEnabled(True)
            self.centralWidget.missionWidget.updateStatusLabel("GUI Configuration", False)

    def saveNotes(self, fileName=''):
        """
                Pulls up Save As dialog, saves notes to designated file and sets filename field
        """
        if fileName == '':
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getSaveFileName(self, 'Save notes',
                                                      self.gui.workspace_path + "/testNotes", "Text Files (*.txt)",
                                                      options=options)
        if fileName:
            if fileName.find(".txt") == -1:
                fileName = fileName + ".txt"

            self.centralWidget.controlsSidebarWidget.noteBoxText = self.centralWidget.controlsSidebarWidget.noteBox.toPlainText()
            with open(fileName, "w") as write_file:
                write_file.write(self.centralWidget.controlsSidebarWidget.noteBoxText)

    @staticmethod
    def openCampaignFolder():
        """
        Opens the OS specific file explorer to where all the campaign data is saved for
        :return: None
        """
        webbrowser.open('file:///' + os.path.realpath(Constants.campaign_data_dir))

    def enterDebug(self):
        """
        Enter debug mode which overrides the gui to attempt to send commands and instead shows what you would see in
        a test
        """
        self.gui.debug_mode = True
        self.debugAct.setDisabled(True)
        self.exitDebugAct.setEnabled(True)
        self.enterEditAct.setDisabled(True)
        self.startRunAct.setDisabled(True)

        self.centralWidget.missionWidget.updateStatusLabel("Debug Mode", True)
        self.gui.setStatusBarMessage("Enter Debug Mode")

    def exitDebug(self):
        """
        Exit debug mode
        """
        self.gui.debug_mode = False
        self.debugAct.setEnabled(True)
        self.exitDebugAct.setDisabled(True)
        self.enterEditAct.setEnabled(True)
        self.startRunAct.setEnabled(True)

        self.centralWidget.missionWidget.updateStatusLabel("GUI Configuration", False)
        self.gui.setStatusBarMessage("Exit Debug Mode")

    def showRunDialog(self, is_test: bool):
        """
        Tell GUI to start a new run or test, and begin that process
        :param is_test: bool specifying if the dialog is for starting a test. If not for starting campaign
        """

        # Create the dialog
        dialog = QDialog(self)
        if is_test:
            dialog.setWindowTitle("Start Test")
        else:
            dialog.setWindowTitle("Start Campaign")

        dialog.setWindowModality(Qt.ApplicationModal)

        # Set dialog size and place in middle of window
        dialog.resize(500*self.gui.pixel_scale_ratio[0], 80*self.gui.pixel_scale_ratio[1])
        dialog.setMinimumWidth(500*self.gui.pixel_scale_ratio[0])
        dialog.move((self.width() - dialog.width()) / 2, (self.height() - dialog.height()) / 2)

        # Create the form layout that will hold the text box
        formLayout = QFormLayout()
        formLayout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)  # This is properly resize textbox on OSX

        # Vertical layout to hold everything
        verticalLayout = QVBoxLayout(dialog)
        verticalLayout.addLayout(formLayout)

        # Create a regular expression validator for the QLineEdit to make sure only characters we want are accepted
        reg_exp = QRegExp("[a-zA-Z0-9 -]+")  # Lower and capital letters, numbers,-, and spaces, at any length (+)
        reg_exp_validator = QRegExpValidator(reg_exp)

        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.default_font)
        font.setPointSize(14 * self.gui.font_scale_ratio)

        # Add in the textbox to give run a title
        textbox = QLineEdit(dialog)
        if is_test:
            textbox.setPlaceholderText("Only number, letters, and spaces")
        else:
            textbox.setPlaceholderText("DATE AUTO ADDED, Only number, letters, and spaces")

        textbox.setValidator(reg_exp_validator)
        textbox.setFont(font)
        if is_test:
            label = QLabel("Test Name:")
        else:
            label = QLabel("Campaign Title:")
        label.setFont(font)
        formLayout.addRow(label, textbox)

        # Horizontal button layout
        buttonLayout = QHBoxLayout()
        
        # Create the buttons, make sure there is no default option, and connect to functions
        cancel_button = QPushButton("Cancel")
        cancel_button.setDefault(False)
        cancel_button.setAutoDefault(False)
        cancel_button.clicked.connect(lambda: self.startRunCanceled(dialog))
        cancel_button.setFont(font)
        cancel_button.setFixedWidth(125 * self.gui.pixel_scale_ratio[0])  # Lazy way to make buttons not full width

        if is_test:
            start_button = QPushButton("Start Test")
            start_button.clicked.connect(lambda: self.startTest(dialog, textbox.text()))
        else:
            start_button = QPushButton("Start Campaign")
            start_button.clicked.connect(lambda: self.startRun(dialog, textbox.text()))

        start_button.setDefault(True)
        start_button.setAutoDefault(False)
        start_button.setFont(font)
        start_button.setFixedWidth(125 * self.gui.pixel_scale_ratio[0])  # Lazy way to make buttons not full width

        buttonLayout.addWidget(cancel_button)
        buttonLayout.addWidget(start_button)

        verticalLayout.addLayout(buttonLayout)

        dialog.show()

    @pyqtSlot(int, str, bool)
    def updateFromConnectionStatus(self, status: int, error_string: str, is_commander: bool):
        """
        Just disables the campaign if the server connection is dropped
        :param status: connection status, 3 is server dropped
        :param error_string: not used
        :param is_commander: not used
        """
        if status == 3:
            self.startRunAct.setDisabled(True)

    def startRun(self, dialog, run_name):
        """
        Start a new run from menu bar and pass in the user inputted name from dialog
        """
        if len(run_name) == 0:
            return

        # When a test is being run we don't want use to be able to edit anything or enter another run
        # Also once a run starts then we want them to have the option to end it
        self.enterEditAct.setDisabled(True)
        self.exitEditAct.setDisabled(True)
        self.startRunAct.setDisabled(True)
        self.endRunAct.setEnabled(True)
        self.debugAct.setDisabled(True)
        self.screenSettingsAct.setDisabled(True)
        self.startTestAct.setEnabled(True)
        self.addAvionicsAct.setDisabled(True)

        self.gui.campaign.startRun(run_name)
        dialog.done(2)  # This 2 is arbitrary expect it differs from the the canceled
        self.gui.setStatusBarMessage("Campaign '" + run_name + "' started")

    def endRun(self):
        """
        Called from a keyboard shortcut or the menu bar, will end run
        """
        # Must ensure that the run is active
        if self.gui.campaign.is_active:
            self.gui.campaign.endRun()

        # Allow editing to happen when run is not active
        self.enterEditAct.setEnabled(True)
        self.endRunAct.setDisabled(True)
        self.startRunAct.setEnabled(True)
        self.screenSettingsAct.setEnabled(True)
        self.screenSettingsAct.setEnabled(True)
        self.startTestAct.setDisabled(True)
        self.endTestAct.setDisabled(True)
        self.addAvionicsAct.setEnabled(True)
        self.debugAct.setEnabled(True)
        self.gui.setStatusBarMessage("Campaign '" + self.gui.campaign.title + "' ended")

    def startTest(self, dialog: QDialog, test_name: str):
        """
        Starts a new test from the menu bar and passes in the user input name. Calls campaign class for the rest of
        the work
        :param dialog: dialog that was created to input name. Needs to be closed properly
        :param test_name: user given name of the test
        """
        if len(test_name) == 0:
            return

        self.endTestAct.setEnabled(True)
        self.startTestAct.setDisabled(True)
        self.gui.campaign.startTest(test_name)  # This 2 is arbitrary expect it differs from the the canceled
        dialog.done(2)
        self.gui.setStatusBarMessage("Test '" + test_name + "' started under the '" + self.gui.campaign.title + "' campaign")

    def endTest(self):
        """
        Ends the test from the menu bar
        """

        self.endTestAct.setDisabled(True)
        self.startTestAct.setEnabled(True)
        self.gui.campaign.endTest()
        self.gui.setStatusBarMessage("Test '" + self.gui.campaign.currentTestName + "' ended")

    @staticmethod  # Idk if this will stay static but for now
    def startRunCanceled(dialog):
        """
        Basically do nothing but close the dialog
        """
        dialog.done(1)  # This 1 is arbitrary

    def showAvionicsDialog(self):
        """
        Show the dialog to configure the avionics that will be connected for the test
        """

        # Create the dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Boards")
        dialog.setWindowModality(Qt.ApplicationModal)

        # Set dialog size and place in middle of window
        dialog.resize(450*self.gui.pixel_scale_ratio[0], 240*self.gui.pixel_scale_ratio[1])
        dialog.setMinimumWidth(450*self.gui.pixel_scale_ratio[0])
        dialog.setMinimumWidth(240*self.gui.pixel_scale_ratio[1])
        dialog.move((self.width() - dialog.width()) / 2, (self.height() - dialog.height()) / 2)

        # Vertical layout to hold everything
        verticalLayout = QVBoxLayout(dialog)

        # Create the form layout that will hold the text box
        formLayout = QFormLayout()
        formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)  # This is properly resize textbox on OSX
        verticalLayout.addLayout(formLayout)

        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.default_font)
        font.setPointSize(14*self.gui.font_scale_ratio)

        # Add in all the dropdowns
        dropdown1 = QComboBox(dialog)
        dropdown1.setFont(font)
        dropdown1.addItems(["None"] + Constants.boards)
        dropdown2 = QComboBox(dialog)
        dropdown2.setFont(font)
        dropdown2.addItems(["None"] + Constants.boards)
        dropdown3 = QComboBox(dialog)
        dropdown3.setFont(font)
        dropdown3.addItems(["None"] + Constants.boards)
        dropdown4 = QComboBox(dialog)
        dropdown4.setFont(font)
        dropdown4.addItems(["None"] + Constants.boards)
        dropdown5 = QComboBox(dialog)
        dropdown5.setFont(font)
        dropdown5.addItems(["None"] + Constants.boards)

        # Array of all the dropdowns
        dropdowns = [dropdown1, dropdown2, dropdown3, dropdown4, dropdown5]

        # If boards are already set, populate the dropdowns
        if self.centralWidget.controlsSidebarWidget.board_objects:
            for i in range(len(self.centralWidget.controlsSidebarWidget.board_objects)):
                dropdowns[i].setCurrentText(self.centralWidget.controlsSidebarWidget.board_objects[i].name)
                self.updateAvionicsDialog(dropdowns, dropdowns[i], i+1)

        # Callback functions
        dropdown1.currentIndexChanged.connect(lambda: self.updateAvionicsDialog(dropdowns, dropdown1, 1))
        dropdown2.currentIndexChanged.connect(lambda: self.updateAvionicsDialog(dropdowns, dropdown2, 2))
        dropdown3.currentIndexChanged.connect(lambda: self.updateAvionicsDialog(dropdowns, dropdown3, 3))
        dropdown4.currentIndexChanged.connect(lambda: self.updateAvionicsDialog(dropdowns, dropdown4, 4))
        dropdown5.currentIndexChanged.connect(lambda: self.updateAvionicsDialog(dropdowns, dropdown5, 5))

        label1 = QLabel("Board 1:")
        label1.setFont(font)
        label2 = QLabel("Board 2:")
        label2.setFont(font)
        label3 = QLabel("Board 3:")
        label3.setFont(font)
        label4 = QLabel("Board 4:")
        label4.setFont(font)
        label5 = QLabel("Board 5:")
        label5.setFont(font)

        # Add to the layout
        formLayout.addRow(label1, dropdown1)
        formLayout.addRow(label2, dropdown2)
        formLayout.addRow(label3, dropdown3)
        formLayout.addRow(label4, dropdown4)
        formLayout.addRow(label5, dropdown5)

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
        save_button.clicked.connect(lambda: self.avionicsDialogSave(dropdowns, dialog))
        save_button.setFixedWidth(125 * self.gui.pixel_scale_ratio[0])

        buttonLayout.addWidget(cancel_button)
        buttonLayout.addWidget(save_button)

        verticalLayout.addLayout(buttonLayout)

        dialog.show()

    @staticmethod
    def updateAvionicsDialog(dropdowns: [], currentDropdown: QComboBox, boxNumber: int):
        """
        This function updates the avionics dialog dropdowns that appears when selecting which boards will be connected
        the run. It ensures that only one of each board is selections, and updates the dropdowns to the available
        boards when possible. This function is called anytime one of the dialog changes
        :param dropdowns: The 5 different dropdowns shown in the dialog
        :param currentDropdown: The current dropdown that was changed
        :param boxNumber: The number of the dropdown that was changed, 1-5
        :return: Returns out when necessary, no return value
        """

        # Checks to make sure a selection is skipped, if it is set the box back to none and return out
        if boxNumber > 1:
            if dropdowns[boxNumber-2].currentIndex() == 0:
                currentDropdown.setCurrentIndex(0)  # 'None' index
                return

        # Every time a dropdown changes, make sure all the ones below them are reset
        for i in range(boxNumber, 5):
                dropdowns[i].clear()
                dropdowns[i].addItems(["None"] + Constants.boards)

        # For each dropdown below the current dropdown, remove any options that have already been selected
        for i in range(5):
            if i > boxNumber-1:
                for j in range(boxNumber):
                    if dropdowns[j].currentIndex() != 0:
                        dropdowns[i].removeItem(dropdowns[j].currentIndex())

    def avionicsDialogSave(self, dropdowns, dialog):
        boards = []
        for i in range(5):
            if dropdowns[i].currentIndex() != 0:
                boards.append(dropdowns[i].currentText())

        # If array is empty
        if not boards:
            return  # Do nothing if the user selected nothing

        self.centralWidget.controlsSidebarWidget.addBoardsToScrollWidget(boards)
        dialog.done(2)

    def showDrawingSettingsDialog(self):
        """
        Show the dialog to configure the avionics that will be connected for the test
        """

        # Create the dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Screen Drawing Settings")
        dialog.setWindowModality(Qt.ApplicationModal)

        # Set dialog size and place in middle of window
        dialog.resize(450*self.gui.pixel_scale_ratio[0], 240*self.gui.pixel_scale_ratio[1])
        dialog.setMinimumWidth(450*self.gui.pixel_scale_ratio[0])
        dialog.setMinimumWidth(240*self.gui.pixel_scale_ratio[1])
        dialog.move((self.width() - dialog.width()) / 2, (self.height() - dialog.height()) / 2)

        # Vertical layout to hold everything
        verticalLayout = QVBoxLayout(dialog)

        # Create the form layout that will hold the text box
        formLayout = QFormLayout()
        formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)  # This is properly resize textbox on OSX
        verticalLayout.addLayout(formLayout)

        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.default_font)
        font.setPointSize(14*self.gui.font_scale_ratio)

        # Create labels and spin boxes
        warningLabel = QLabel("WARNING: REQUIRES GUI REBOOT")
        warningLabel.setStyleSheet("color: red")
        warningLabel.setAlignment(Qt.AlignCenter)
        font2 = QFont()
        font2.setStyleStrategy(QFont.PreferAntialias)
        font2.setFamily(Constants.default_font)
        font2.setBold(True)
        font2.setPointSizeF(20*self.gui.font_scale_ratio)
        warningLabel.setFont(font2)

        font_label = QLabel("Font Scale:")
        font_label.setFont(font)

        font_spinBox = QDoubleSpinBox(self)
        font_spinBox.setMinimum(.1)
        font_spinBox.setMaximum(5)
        font_spinBox.setSingleStep(.1)
        font_spinBox.setFont(font)
        font_spinBox.setValue(self.gui.font_scale_ratio)

        pixel_label = QLabel("Pixel Scale:")
        pixel_label.setFont(font)

        pixel_spinBox = QDoubleSpinBox(self)
        pixel_spinBox.setMinimum(.1)
        pixel_spinBox.setMaximum(5)
        pixel_spinBox.setSingleStep(.1)
        pixel_spinBox.setFont(font)
        pixel_spinBox.setValue(self.gui.pixel_scale_ratio[0])

        line_label = QLabel("Line Width:")
        line_label.setFont(font)

        line_spinBox = QSpinBox(self)
        line_spinBox.setMinimum(1)
        line_spinBox.setMaximum(6)
        line_spinBox.setSingleStep(1)
        line_spinBox.setFont(font)
        line_spinBox.setValue(Constants.line_width)

        formLayout.addRow(warningLabel)
        formLayout.addRow(pixel_label,pixel_spinBox)
        formLayout.addRow(font_label, font_spinBox)
        formLayout.addRow(line_label,line_spinBox)

        # TODO: Make a little viewer to see the changes before applying them

        # Horizontal button layout
        buttonLayout = QHBoxLayout()
        # Create the buttons, make sure there is no default option, and connect to functions
        cancel_button = QPushButton("Cancel")
        cancel_button.setFont(font)
        cancel_button.setDefault(False)
        cancel_button.setAutoDefault(False)
        cancel_button.clicked.connect(lambda: dialog.done(1))
        cancel_button.setFixedWidth(125 * self.gui.pixel_scale_ratio[0])  # Lazy way to make buttons not full width

        save_button = QPushButton("Reboot")
        save_button.setFont(font)
        save_button.setDefault(False)
        save_button.setAutoDefault(False)
        save_button.clicked.connect(lambda: self.updateScreenDrawSettings(dialog, pixel_spinBox.value(), font_spinBox.value(), line_spinBox.value()))
        save_button.setFixedWidth(125 * self.gui.pixel_scale_ratio[0])

        buttonLayout.addWidget(cancel_button)
        buttonLayout.addWidget(save_button)

        verticalLayout.addLayout(buttonLayout)

        dialog.show()

    def showStandardMessageDialog(self, title: str, text: str, icon: str = None):
        """
        Shows a standard dialog with just an OK button. Used rarely when something happens in the background the user
        would not know unless paying very close attention
        :param title: dialog window title
        :param text: text of the dialog
        :param icon: optional string to specify what the icon should be. Can be NoIcon, Question, Information, Warning,
        Critical
        """

        msgBox = QMessageBox(self)
        if icon is None or icon == "NoIcon":
            msgBox.setIcon(QMessageBox.NoIcon)
        elif icon == "Warning":
            msgBox.setIcon(QMessageBox.Warning)
        elif icon == "Information":
            msgBox.setIcon(QMessageBox.Information)
        elif icon == "Critical":
            msgBox.setIcon(QMessageBox.Critical)
        elif icon == "Question":
            msgBox.setIcon(QMessageBox.Question)

        msgBox.setText(text)
        msgBox.setWindowTitle(title)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.show()

    def updateScreenDrawSettings(self, dialog, new_pixel_scale, new_font_scale, new_line_scale):
        """
        This function is called when the user clicks reboot in above dialog, updates the screen settings, saves them to
        file and then calls for a reboot
        :param dialog: dialog that is open, used so it can be properly closed
        :param new_pixel_scale: new scale for pixels on screen
        :param new_font_scale: new font scale
        :param new_line_scale: new line width value
        """
        # Close dialog
        dialog.done(2)

        # The user only updates the x pixel scale ratio, must keep things square so this updates y
        pixel_scale_change = new_pixel_scale/self.gui.pixel_scale_ratio[0] * self.gui.pixel_scale_ratio[1]
        self.gui.pixel_scale_ratio = [new_pixel_scale, pixel_scale_change]

        # Update other visual settings
        self.gui.font_scale_ratio = new_font_scale
        Constants.line_width = new_line_scale

        # Save the gui preferences and reboot
        self.gui.savePreferences()
        QCoreApplication.exit(self.gui.EXIT_CODE_REBOOT)

    def ambientizeCmd(self, action: QAction):
        """
        Sends command to ambientize pts
        :param action: Qaction that was clicked
        :return:
        """
        cmd_dict = {
            "function_name": "ambientize_pressure_transducers",
            "target_board_addr": self.interface.getBoardAddr(action.text()),
            "timestamp": int(datetime.now().timestamp()),
            "args": []
        }
        # print(cmd_dict)
        self.gui.liveDataHandler.sendCommand(3, cmd_dict)

    def tareLoadCell(self):
        """
        Sends command to tare load cells
        :param action: Qaction that was clicked
        :return:
        """
        cmd_dict = {
            "function_name": "tare_load_cells",
            "target_board_addr": 0,
            "timestamp": int(datetime.now().timestamp()),
            "args": []
        }
        # print(cmd_dict)
        self.gui.liveDataHandler.sendCommand(3, cmd_dict)

    def zeroSystemClock(self):
        cmd_dict = {
            "function_name": "set_system_clock",
            "target_board_addr": 3,
            "timestamp": int(datetime.now().timestamp()),
            "args": [0]
        }
        # print(cmd_dict)
        self.gui.liveDataHandler.sendCommand(3, cmd_dict)
        cmd_dict = {
            "function_name": "set_system_clock",
            "target_board_addr": 0,
            "timestamp": int(datetime.now().timestamp()),
            "args": [0]
        }
        # print(cmd_dict)
        self.gui.liveDataHandler.sendCommand(3, cmd_dict)

    @overrides
    def closeEvent(self, event):
        """
        Called when the window is closed
        :param event: window close event
        :return: none
        """
        self.gui.guiExit()


class ControlsCentralWidget(QWidget):
    """
    Window to house the controls and editing Widgets
    """

    def __init__(self, parent=None, window=None):
        super().__init__()
        self.parent = parent
        self.gui = parent.gui
        self.window = window

        self.left = 0
        self.top = 0
        self.width = self.gui.screenResolution[0]
        if self.gui.platform == "Windows":
            self.height = self.window.height() - self.parent.statusBar().height()
        else:
            self.height = self.window.height()

        self.setGeometry(self.left, self.top, self.width, self.height)

        # Width of the panel on the right hand side
        # HMM: Should this go here or in the ControlsPanelWidget Class?
        self.panel_width = 300 * self.gui.pixel_scale_ratio[0]
        self.status_bar_height = self.parent.statusBar().height()

        # Marker for if the controls area is being edited
        self.is_editing = False
        self.controlsWidget = ControlsWidget(self)
        self.controlsPanelWidget = ControlsPanelWidget(self)
        self.controlsSidebarWidget = ControlsSidebarWidget(self)
        self.missionWidget = MissionWidget(self)

        # Some variables depend on the init of ControlsPanelWidget so has to happen after it inits
        self.controlsWidget.finalizeInit()

    @overrides
    def resizeEvent(self, e: QResizeEvent):
        """
        Called when window is re-sized, updates height and width values

        :param e: variable holding event data
        """
        self.width = self.size().width()
        self.height = self.size().height()
