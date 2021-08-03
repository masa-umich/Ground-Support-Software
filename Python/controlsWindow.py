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
from flash import FlashDialog
from abort_button import AbortButton
from limits import LimitWindow
from auto_manager import AutoManager
from dp import TankLevelDialog

#from sensor_calibrations import SensorCalibrationDialog

from overrides import overrides
import os
import ctypes
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
        self.client_dialog = ClientDialog(True, self) # control client
        self.last_packet = {}
        self.interface = S2_Interface()
        self.statusBar().setFixedHeight(22 * self.gui.pixel_scale_ratio[1])
        self.centralWidget = ControlsCentralWidget(self, self)
        self.setCentralWidget(self.centralWidget)
        self.fileName = ""
        self.setWindowTitle(self.title)
        self.setGeometry(self.centralWidget.left, self.centralWidget.top, self.centralWidget.width, self.centralWidget.height)
        self.flash_dialog = FlashDialog(self.client_dialog.client)
        self.button_box = AbortButton(self.client_dialog.client)
        self.limits = LimitWindow(8, self.client_dialog.client)
        self.auto_manager = AutoManager(self.client_dialog.client)
        self.tank_levels = TankLevelDialog(dual=False)
        #self.sensor_calibration = None
        self.data_viewer_dialog = DataViewerDialog(self.gui)
        self.scrollArea = None
        self.lower_voltage = []
        self.upper_voltage = []
        self.upper_pressure = []
        self.channel_count = 0

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
        exitAct.triggered.connect(qApp.quit)

        # The next several segments of code create objects to represent each button action for the toolbar
        # Each segment has a comment above it describing what action it implements
        # The third line of each segment calls a function, defined below, that carries out the action of the button
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

        # FILE -> Save Notes
        self.saveNotesAct = QAction('&Save notes', self)                                                                                                                                                                                                                                                                                                                                                                                                            
        self.saveNotesAct.triggered.connect(self.saveNotes)

        # Run -> Add Boards
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
        self.exitEditAct.setDisabled(True) # Start with it disabled

        # Run -> Start Run
        self.startRunAct = QAction('&Start Run', self)
        self.startRunAct.setShortcut('Ctrl+R')
        self.startRunAct.triggered.connect(self.showRunDialog)

        # Run -> End Run
        self.endRunAct = QAction('&End Run', self)
        self.endRunAct.setShortcut('Ctrl+Shift+R')
        self.endRunAct.triggered.connect(self.endRun)
        self.endRunAct.setDisabled(True)  # Start with it disabled

        # Run -> Add Boards
        self.addAvionicsAct = QAction('&Add Avionics', self)
        self.addAvionicsAct.triggered.connect(self.showAvionicsDialog)
        self.addAvionicsAct.setShortcut('Alt+A')

        # Run -> Connection Settings
        self.connect = QAction("&Connection", self)
        self.connect.triggered.connect(lambda: self.show_window(self.client_dialog))
        self.connect.setShortcut('Alt+C')

        # Run -> Connection Settings
        data_view_dialog = QAction("&Data Viewer", self)
        data_view_dialog.triggered.connect(lambda: self.show_window(self.data_viewer_dialog))

        # Run -> Flash
        self.flashsettings = QAction("&Flash", self)
        self.flashsettings.triggered.connect(lambda: self.show_window(self.flash_dialog))
        self.flashsettings.setShortcut('Alt+F')

        # Run -> Checkpoint Log
        self.checkpointAct = QAction('Checkpoint &Log', self)
        self.checkpointAct.setShortcut('Ctrl+L')
        self.checkpointAct.triggered.connect(self.checkpoint)

        #Run -> Tare Load Cells
        self.tareLoadCellAct = QAction('Tare GSE Load Cells', self)
        self.tareLoadCellAct.triggered.connect(self.tareLoadCell)

        # Run -> Zero Board System Time
        self.zeroTimeAct = QAction('Zero Board System Clocks', self)
        self.zeroTimeAct.triggered.connect(self.zeroSystemClock)


        # Run -> Abort Button Settings
        self.buttonBoxAct = QAction('Abort &Button', self)
        self.buttonBoxAct.setShortcut('Alt+B')
        self.buttonBoxAct.triggered.connect(lambda: self.show_window(self.button_box))

        # Run -> Limits
        self.limit_action = QAction('&Limits', self)
        self.limit_action.triggered.connect(lambda: self.show_window(self.limits))
        self.limit_action.setShortcut('Alt+L')

        # Run -> Autosequence Manager
        self.auto_action = QAction('Auto&sequence Manager', self)
        self.auto_action.triggered.connect(lambda: self.show_window(self.auto_manager))
        self.auto_action.setShortcut('Alt+S')

        self.ambientizeMenu = QMenu('Ambientize',self)
        self.ambientizeMenu.triggered.connect(self.ambientizeCmd)
        for board in Constants.boards:
            self.ambientizeMenu.addAction(board)

        # Run -> Level Sensing
        self.level_action = QAction("&Level Sensing", self)
        self.level_action.triggered.connect(lambda: self.show_window(self.tank_levels))
        #self.level_action.setShortcut('Alt+D')

        #Run -> Sensor Calibrations
        self.sensor_calibration = QMenu("Sensor Calibrations", self)
        self.sensor_calibration.triggered.connect(self.calibrateSensorsWindow)
        for board in Constants.boards:
            self.sensor_calibration.addAction(board)

        # Creates menu bar, adds tabs file, edit, view
        menuBar = self.menuBar()
        menuBar.setNativeMenuBar(True)
        menuBar.setStyleSheet("background-color:white;border:0;color:black;")
        file_menu = menuBar.addMenu('File')
        edit_menu = menuBar.addMenu('Edit')
        #view_menu = menuBar.addMenu('View')
        run_menu = menuBar.addMenu('Run')

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
        file_menu.addAction(self.saveNotesAct)

        # Adds all the edit button to the edit tab
        edit_menu.addAction(self.enterEditAct)
        edit_menu.addAction(self.exitEditAct)

        # Adds any related run buttons to the run tab
        run_menu.addAction(self.startRunAct)
        run_menu.addAction(self.endRunAct)
        run_menu.addAction(self.addAvionicsAct)
        run_menu.addAction(self.checkpointAct)
        run_menu.addAction(data_view_dialog)
        run_menu.addMenu(self.ambientizeMenu)
        run_menu.addAction(self.tareLoadCellAct)
        run_menu.addAction(self.zeroTimeAct)

        # If the gui is being run on windows, dont use the menu bar
        if self.gui.platform == "Windows":
            menuBar.addAction(self.connect)
            menuBar.addAction(self.flashsettings)
            menuBar.addAction(self.buttonBoxAct)
            menuBar.addAction(self.limit_action)
            menuBar.addAction(self.auto_action)
            menuBar.addAction(self.level_action)
            menuBar.addMenu(self.sensor_calibration)
        elif self.gui.platform == "OSX":
            run_menu.addAction(self.connect)
            run_menu.addAction(self.flashsettings)
            run_menu.addAction(self.buttonBoxAct)
            run_menu.addAction(self.limit_action)
            run_menu.addAction(self.auto_action)
            run_menu.addAction(self.level_action)
            run_menu.addMenu(self.sensor_calibration)

        # Add all menus to a dict for easy access by other functions
        self.menus = {"File": file_menu,
                      "Edit": edit_menu,
                      #"View": view_menu,
                      "Run":  run_menu}
        
        self.showMaximized()

        # I have no clue why this is so strange, but see update function for more info
        self.central_widget_offset = None


            
    def saveRegular(self):
        """
        Executes the save action. If file is named, just runs saveData.
        If file is not yet named, executes Save As action.
        """
        if self.fileName != "":
            self.centralWidget.controlsWidget.saveData(self.fileName)
        else:
            self.saveFileDialog()
            self.saveNotes()
    
    def checkpoint(self):
        if not self.gui.run.is_active:
            self.client_dialog.client.command(6, None)

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

    def newFile(self):
        """
        Creates new blank untitled file. Basically just erases everything and sets filename to unset
        """
        self.fileName = ""
        self.centralWidget.controlsPanelWidget.removeAllEditingObjects()
        length = len(self.centralWidget.controlsWidget.object_list)
        for i in range(length):
            self.centralWidget.controlsWidget.deleteObject(self.centralWidget.controlsWidget.object_list[0])

        for tube in self.centralWidget.controlsWidget.tube_list:
            tube.deleteTube()

        self.statusBar().showMessage("New configuration started")

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
            self.statusBar().showMessage("Enter Edit Mode")

    def exitEdit(self):
        """
        Same as enter edit mode, but the opposite
        """
        if self.centralWidget.is_editing:
            self.centralWidget.controlsWidget.toggleEdit()
            self.centralWidget.controlsPanelWidget.hide()
            self.centralWidget.controlsSidebarWidget.show()
            self.enterEditAct.setEnabled(True)
            self.exitEditAct.setDisabled(True)
            self.debugAct.setEnabled(True)
            self.exitDebugAct.setEnabled(True)
            self.startRunAct.setEnabled(True)
            self.statusBar().showMessage("Exit Edit Mode")

    def saveNotes(self):
        """
                Pulls up Save As dialog, saves notes to designated file and sets filename field
        """
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




    def enterDebug(self):
        """
        Enter debug mode which overrides the gui to attempt to send commands and instead shows what you would see in
        a test
        """
        self.gui.debug_mode = True
        self.debugAct.setDisabled(True)
        self.exitDebugAct.setEnabled(True)
        self.startRunAct.setDisabled(True)

        self.centralWidget.missionWidget.updateStatusLabel("Debug Mode", True)
        self.statusBar().showMessage("Enter Debug Mode")

    def exitDebug(self):
        """
        Exit debug mode
        """
        self.gui.debug_mode = False
        self.debugAct.setEnabled(True)
        self.exitDebugAct.setDisabled(True)
        self.startRunAct.setEnabled(True)

        self.centralWidget.missionWidget.updateStatusLabel("GUI Configuration", False)
        self.statusBar().showMessage("Exit Debug Mode")

    def showRunDialog(self):
        """
        Tell GUI to start a new run or test, and begin that process
        """

        # Create the dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Start Run")
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
        textbox.setPlaceholderText("DATE AUTO ADDED, Only number, letters, and spaces")
        textbox.setValidator(reg_exp_validator)
        textbox.setFont(font)
        label = QLabel("Run Title:")
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

        start_button = QPushButton("Start Run")
        start_button.setDefault(False)
        start_button.setAutoDefault(False)
        start_button.clicked.connect(lambda: self.startRun(dialog, textbox.text()))
        start_button.setFont(font)
        start_button.setFixedWidth(125 * self.gui.pixel_scale_ratio[0])  # Lazy way to make buttons not full width

        buttonLayout.addWidget(cancel_button)
        buttonLayout.addWidget(start_button)

        verticalLayout.addLayout(buttonLayout)

        dialog.show()

    def startRun(self, dialog, run_name):
        """
        Start a new run from menu bar and pass in the user inputted name from dialog
        """
        # When a test is being run we don't want use to be able to edit anything or enter another run
        # Also once a run starts then we want them to have the option to end it
        self.enterEditAct.setDisabled(True)
        self.exitEditAct.setDisabled(True)
        self.startRunAct.setDisabled(True)
        self.endRunAct.setEnabled(True)
        self.screenSettingsAct.setDisabled(True)

        self.gui.run.startRun(run_name)
        dialog.done(2)  # This 2 is arbitrary expect it differs from the the canceled
        self.statusBar().showMessage("Run: " + run_name + " started")

    def endRun(self):
        """
        Called from a keyboard shortcut or the menu bar, will end run
        """
        # Must ensure that the run is active
        if self.gui.run.is_active:
            self.gui.run.endRun()

        # Allow editing to happen when run is not active
        self.enterEditAct.setEnabled(True)
        self.endRunAct.setDisabled(True)
        self.startRunAct.setEnabled(True)
        self.screenSettingsAct.setEnabled(True)
        self.screenSettingsAct.setEnabled(True)
        self.statusBar().showMessage("Run: " + self.gui.run.title + " ended")

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
        dialog.setWindowTitle("Add Avionics")
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
        if self.gui.run.boards:
            for i in range(len(self.gui.run.boards)):
                dropdowns[i].setCurrentText(self.gui.run.boards[i])
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

        # Set the run to have these boards attached
        self.gui.run.boards = boards

        self.centralWidget.controlsSidebarWidget.addBoards(boards)
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

    def updateScreenDrawSettings(self, dialog, new_pixel_scale, new_font_scale, new_line_scale):
        """
        This function is called when the user clicks reboot in above dialog, updates the screen settings, saves them to
        file and then calls for a reboot
        :param new_pixel_scale: new scale for pixels on screen
        :param new_font_scale: new font scale
        :param new_line_scale: new line width value
        """
        # Close dialog
        dialog.done(2)

        # The user only updates the x pixel scale ratio, must keep things square so this updates y
        pixel_scale_change = self.gui.pixel_scale_ratio[0]/new_pixel_scale * self.gui.pixel_scale_ratio[1]
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
        self.client_dialog.client.command(3, cmd_dict)

    #def openCalibrationSensorsWindow(self, action: QAction):
     #   self.sensor_calibration = SensorCalibrationDialog(action.text())
      #  self.show_window(self.sensor_calibration)


    def calibrateSensorsWindow(self, action: QAction):
        #EC: 20
        #Press: 6
        #GSE controller: 22


        channel_settings = ["pt_cal_lower_voltage","pt_cal_upper_voltage", "pt_cal_upper_pressure"]
        dialog = QDialog(self)
        dialog.setWindowTitle("Sensor Channels")
        dialog.setWindowModality(Qt.ApplicationModal)
        self.channel_count = 0



        # Vertical layout to hold everything
        verticalLayout = QGridLayout(dialog)



        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.default_font)
        font.setPointSize(14 * self.gui.font_scale_ratio)

        if (action.text() == "Pressurization Controller"):
            self.channel_count = 6
        elif(action.text() == "Flight Computer"):
            print(action.text())
        elif (action.text() == "Engine Controller"):
            self.channel_count = 20
        elif (action.text() == "Recovery Controller"):
            print(action.text())
        elif (action.text() == "GSE Controller"):
            self.channel_count = 22



        #probably make a global channel var to store all the calibrations to load in
        #or make a function to refresh the channels that passes in one setting/count at a time and call it here
        #ask how refresh channel works
        end = 0
        for x in range(self.channel_count):
            # Create the form layout that will hold the text box
            formLayout = QtWidgets.QGridLayout()
            labelLayout =QtWidgets.QGridLayout()


            lower_voltage_box = QDoubleSpinBox()
            lower_voltage_box.setMaximum(9999)
            lower_voltage_box.setValue(0)
            lower_voltage_box.setDecimals(2)


            upper_voltage_box = QDoubleSpinBox()
            upper_voltage_box.setMaximum(9999)
            upper_voltage_box.setValue(0)
            upper_voltage_box.setDecimals(2)

            upper_pressure_box = QDoubleSpinBox()
            upper_pressure_box.setMaximum(9999)
            upper_pressure_box.setValue(0)
            upper_pressure_box.setDecimals(0)

            self.lower_voltage.append(lower_voltage_box)
            self.upper_voltage.append(upper_voltage_box)
            self.upper_pressure.append(upper_pressure_box)

            label = QLabel("PT Channel " + str(x))
            label.setFont(font)

            label_buffer = QLabel("              ")
            label1 = QLabel("Lower Voltage")
            label2 = QLabel("Upper Voltage")
            label3 = QLabel("Pressure Range")
            font.setPointSize(18 * self.gui.font_scale_ratio)
            label.setFont(font)
            label1.setFont(font)
            label2.setFont(font)
            label3.setFont(font)

            labelLayout.addWidget(label_buffer, 0, 1)
            labelLayout.addWidget(label1, 0, 2)
            labelLayout.addWidget(label2, 0, 3)
            labelLayout.addWidget(label3, 0, 4)


            formLayout.addWidget(label, 0, 1)
            formLayout.addWidget(lower_voltage_box, 0, 2)
            formLayout.addWidget(upper_voltage_box, 0, 3)
            formLayout.addWidget(upper_pressure_box, 0, 4)

            verticalLayout.addLayout(labelLayout, 2 * x + 1, 0)
            verticalLayout.addLayout(formLayout,2*x + 2,0)
            #verticalLayout.setColumnStretch(x, 20)

            end = 2*x + 2

        end +=1

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(dialog)
        self.scrollArea.setWidgetResizable(True)
        self. scrollArea.setFixedHeight(1000*self.gui.pixel_scale_ratio[0])
        self.scrollArea.setFixedWidth(800*self.gui.pixel_scale_ratio[0])


        #Horizontal button layout
        buttonLayout = QHBoxLayout()
        # Create the buttons, make sure there is no default option, and connect to functions
        cancel_button = QPushButton("Cancel")
        cancel_button.setFont(font)
        cancel_button.setDefault(False)
        cancel_button.setAutoDefault(False)
        cancel_button.clicked.connect(lambda: dialog.done(1))
        cancel_button.setFixedWidth(125 * self.gui.pixel_scale_ratio[0])  # Lazy way to make buttons not full width

        font.setPointSize(20 * self.gui.font_scale_ratio)

        save_button = QPushButton("Save")
        save_button.setFont(font)
        save_button.setDefault(False)
        save_button.setAutoDefault(False)
        save_button.clicked.connect(lambda: self.send_sensor_calibrations(action.text()))
        save_button.setFixedWidth(300 * self.gui.pixel_scale_ratio[0])

        refresh_button = QPushButton("Refresh")
        refresh_button.setFont(font)
        refresh_button.setDefault(False)
        refresh_button.setAutoDefault(False)
        refresh_button.clicked.connect(lambda: self.get_calibrate_sensors(action.text()))
        refresh_button.setFixedWidth(300 * self.gui.pixel_scale_ratio[0])  # Lazy way to make buttons not full

        #buttonLayout.addWidget(cancel_button)
        buttonLayout.addWidget(save_button)
        buttonLayout.addWidget(refresh_button)

        verticalLayout.addLayout(buttonLayout, 0, 0)
        #self.get_calibrate_sensors(action.text())


        dialog.show()
        self.scrollArea.show()
        #sys.exit(app.exec_())
        #self.show_window(scrollArea)

    def send_sensor_calibrations(self,board_name):
        timeout = 0.5
        prefix = self.interface.getPrefix(board_name)
        for x in range(self.channel_count):
            cmd_dict = {
                "function_name": "set_pt_lower_voltage",
                "target_board_addr": self.interface.getBoardAddr(board_name),
                "timestamp": int(datetime.now().timestamp()),
                "args": [x,self.lower_voltage[x].value()]
            }
            self.client_dialog.client.command(3, cmd_dict)
            cmd_dict = {
                "function_name": "set_pt_upper_voltage",
                "target_board_addr": self.interface.getBoardAddr(board_name),
                "timestamp": int(datetime.now().timestamp()),
                "args": [x,self.upper_voltage[x].value()]
            }
            self.client_dialog.client.command(3, cmd_dict)
            cmd_dict = {
                "function_name": "set_pt_upper_pressure",
                "target_board_addr": self.interface.getBoardAddr(board_name),
                "timestamp": int(datetime.now().timestamp()),
                "args": [x,self.upper_pressure[x].value()]
            }
            self.client_dialog.client.command(3, cmd_dict)


    def get_calibrate_sensors(self, board_name):
        packet = None
        timeout = 0.5
        prefix = self.interface.getPrefix(board_name)
        cmd_dict = {
            "function_name": "refresh_calibrations",
            "target_board_addr": self.interface.getBoardAddr(board_name),
            "timestamp": int(datetime.now().timestamp()),
            "args": []
        }
        self.client_dialog.client.command(3, cmd_dict)
        #while True:
        #    if time.time() > timeout:
        #        break
        time.sleep(timeout)  # Wait for the refresh to finish

        for x in range(self.channel_count):
            self.lower_voltage[x].setValue(self.last_packet[prefix + "pt_cal_lower_voltage[" + str(x) +"]"])
            self.upper_voltage[x].setValue(self.last_packet[prefix + "pt_cal_upper_voltage[" + str(x) + "]"])
            self.upper_pressure[x].setValue(self.last_packet[prefix + "pt_cal_upper_pressure[" + str(x) + "]"])


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
        self.client_dialog.client.command(3, cmd_dict)

    def zeroSystemClock(self):
        cmd_dict = {
            "function_name": "set_system_clock",
            "target_board_addr": 3,
            "timestamp": int(datetime.now().timestamp()),
            "args": [0]
        }
        # print(cmd_dict)
        self.client_dialog.client.command(3, cmd_dict)
        cmd_dict = {
            "function_name": "set_system_clock",
            "target_board_addr": 0,
            "timestamp": int(datetime.now().timestamp()),
            "args": [0]
        }
        # print(cmd_dict)
        self.client_dialog.client.command(3, cmd_dict)
    
    def show_window(self, window: QWidget):
        """Shows a window or brings it to the front if already open.

        Args:
            window (QWidget): window to show
        """
        # open window
        window.show()

        # bring to front
        window.setWindowState(window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        window.activateWindow()

    @overrides
    def update(self):
        super().update()

        # So the window does not move to its final position till after exec_ is called on the gui, which means it cannot
        # go in the init_ function. This seems very strange but this appears to be the best solution
        if self.central_widget_offset is None:
            # Not sure why this is different, but seems to due with the fact that windows handles central widget differently
            if self.gui.platform == "Windows":
                self.central_widget_offset = self.centralWidget.pos() - self.pos() + QPoint(0, self.menuBar().height())
            elif self.gui.platform == "OSX":
                self.central_widget_offset = self.pos()

        packet = self.client_dialog.client.cycle()
        if packet != None: # on exception
            self.last_packet = packet
        
        self.centralWidget.update()

        self.button_box.cycle()
        self.limits.update_limits(self.last_packet)
        self.tank_levels.update_values(self.last_packet)
        self.flash_dialog.flash_controller.update(self.last_packet)

        # checks whether the button is enabled relative to the abort button settings menu
        if self.button_box.is_soft_armed:
            self.centralWidget.controlsSidebarWidget.abort_button_enabled = True
        else:
            self.centralWidget.controlsSidebarWidget.abort_button_enabled = False




class ControlsCentralWidget(QWidget):
    """
    Window to house the controls and editing Widgets
    """

    def __init__(self, parent=None, window=None):
        super().__init__()
        self.parent = parent
        self.gui = parent.gui
        self.window = window

        # Below numbers are arbitrary
        # TODO: Make them not arbitrary
        self.left = 0
        self.top = 0
        self.width = self.gui.screenResolution[0]
        self.height = self.gui.screenResolution[1]*.9

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
    def update(self):
        super().update()
        self.controlsWidget.update()
        self.controlsSidebarWidget.update()
        self.missionWidget.update()

    @overrides
    def resizeEvent(self, e: QResizeEvent):
        """
        Called when window is re-sized, updates height and width values

        :param e: variable holding event data
        """
        self.width = self.size().width()
        self.height = self.size().height()