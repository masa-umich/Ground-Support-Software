from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from controlsWidget import ControlsWidget
from controlsPanelWidget import ControlsPanelWidget
from missionWidget import MissionWidget
from ClientWidget import ClientWidget, ClientDialog

from overrides import overrides

"""
This file contains the class to create the main window
"""

class ControlsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        # Set geometry
        self.gui = parent
        self.title = 'MASA Console'
        self.setWindowIcon(QIcon('M_icon.png'))
        self.client_dialog = ClientDialog(True) # control client
        self.centralWidget = ControlsCentralWidget(self, self)
        self.setCentralWidget(self.centralWidget)
        self.fileName = ""
        self.setWindowTitle(self.title)
        self.setGeometry(self.centralWidget.left, self.centralWidget.top, self.centralWidget.width, self.centralWidget.height)


        # Menu system, probably should be its own function, allows things to be placed in menu bar at top of application
        exitAct = QAction('&Save and Quit', self)
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        # The next several segments of code create objects to represent each button action for the toolbar
        # Each segment has a comment above it describing what action it implements
        # The third line of each segment calls a function, defined below, that carries out the action of the button

        # FILE -> New
        newAct = QAction('&New', self)
        newAct.setShortcut('Ctrl+N')
        newAct.triggered.connect(self.newFile)

        # FILE -> Open
        openAct = QAction('&Open', self)
        openAct.setShortcut('Ctrl+O')
        openAct.triggered.connect(self.openFileDialog)

        # FILE -> Save
        saveAct = QAction('&Save', self)
        saveAct.setShortcut('Ctrl+S')
        saveAct.triggered.connect(self.saveRegular)

        # FILE -> Save As
        saveAsAct = QAction('&Save As', self)
        saveAsAct.setShortcut('Ctrl+Shift+S')
        saveAsAct.triggered.connect(self.saveFileDialog)

        # TODO: We should have exit and enter as options only when possible, ie can't exit if u haven't started
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

        # CONNECTION -> Connection Settings
        connect = QAction("&Connection Settings", self)
        connect.triggered.connect(self.client_dialog.show)
        
        # Creates menu bar, adds tabs file, edit, view
        menuBar = self.menuBar()
        menuBar.setNativeMenuBar(True)
        file_menu = menuBar.addMenu('File')
        edit_menu = menuBar.addMenu('Edit')
        view_menu = menuBar.addMenu('View')
        run_menu = menuBar.addMenu('Run')
        connection_menu = menuBar.addMenu('Connection')

        # Adds all the file buttons to the file tab
        file_menu.addAction(newAct)
        file_menu.addAction(openAct)
        file_menu.addAction(saveAct)
        file_menu.addAction(saveAsAct)
        file_menu.addAction(exitAct)

        # Adds all the edit button to the edit tab
        edit_menu.addAction(self.enterEditAct)
        edit_menu.addAction(self.exitEditAct)

        # Adds any related run buttons to the run tab
        run_menu.addAction(self.startRunAct)
        run_menu.addAction(self.endRunAct)

        # add connection actions
        connection_menu.addAction(connect)

        # Add all menus to a dict for easy access by other functions
        self.menus = {"File": file_menu,
                      "Edit": edit_menu,
                      "View": view_menu,
                      "Run":  run_menu,
                      "Connection": connection_menu}
        
        self.showMaximized()

    def saveRegular(self):
        """
        Executes the save action. If file is named, just runs saveData.
        If file is not yet named, executes Save As action.
        """
        if self.fileName != "":
            self.centralWidget.controlsWidget.saveData(self.fileName)
        else:
            self.saveFileDialog()

    def saveFileDialog(self):
        """
        Pulls up Save As dialog, saves data to designated file and sets filename field
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, 'Save File', self.fileName, "JSON Files (*.json)", options=options)
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
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "JSON Files (*.json)", options=options)
        if fileName:
            self.newFile()
            self.fileName = fileName
            self.centralWidget.controlsWidget.loadData(fileName)

    def newFile(self):
        """
        Creates new blank untitled file. Basically just erases everything and sets filename to unset
        """
        self.fileName = ""
        length = len(self.centralWidget.controlsWidget.object_list)
        for i in range(length):
            print(self.centralWidget.controlsWidget.object_list[0].serial_number)
            self.centralWidget.controlsWidget.deleteObject(self.centralWidget.controlsWidget.object_list[0])

        self.centralWidget.controlsWidget.tube_list = []

    def enterEdit(self):
        """
        If not already editing, calls toggle edit to enter edit mode
        """
        if not self.centralWidget.is_editing:
            #self.centralWidget.controlsPanelWidget.show()
            self.centralWidget.controlsWidget.toggleEdit()
            self.enterEditAct.setDisabled(True)
            self.exitEditAct.setEnabled(True)

    def exitEdit(self):
        """
        Same as enter edit mode, but the opposite
        """
        if self.centralWidget.is_editing:
            self.centralWidget.controlsWidget.toggleEdit()
            #self.centralWidget.controlsPanelWidget.hide()
            self.enterEditAct.setEnabled(True)
            self.exitEditAct.setDisabled(True)

    def showRunDialog(self):
        """
        Tell GUI to start a new run or test, and begin that process
        """

        # Create the dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Start Run")
        dialog.setWindowModality(Qt.ApplicationModal)

        # Set dialog size and place in middle of window
        dialog.resize(450, 80)
        dialog.setMinimumWidth(450)
        dialog.setFixedHeight(80)
        dialog.move((self.width() - dialog.width()) / 2, (self.height() - dialog.height()) / 2)

        # Create the form layout that will hold the text box
        formLayout = QFormLayout(dialog)
        formLayout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)  # This is properly resize textbox on OSX

        # Create a regular expression validator for the QLineEdit to make sure only characters we want are accepted
        reg_exp = QRegExp("[a-zA-Z0-9 -]+")  # Lower and capital letters, numbers,-, and spaces, at any length (+)
        reg_exp_validator = QRegExpValidator(reg_exp)

        # Add in the textbox to give run a title
        textbox = QLineEdit(dialog)
        textbox.setPlaceholderText("DATE AUTO ADDED, Only number, letters, and spaces")
        textbox.setValidator(reg_exp_validator)
        formLayout.addRow("Run Title:", textbox)
        
        # Create the buttons, make sure there is no default option, and connect to functions
        cancel_button = QPushButton("Cancel", dialog)
        cancel_button.setDefault(False)
        cancel_button.setAutoDefault(False)
        cancel_button.clicked.connect(lambda: self.startRunCanceled(dialog))

        start_button = QPushButton("Start Run", dialog)
        start_button.setDefault(False)
        start_button.setAutoDefault(False)
        start_button.clicked.connect(lambda: self.startRun(dialog, textbox.text()))

        # Move the buttons into position, and show them
        cancel_button.move((dialog.width() - 2 * cancel_button.width()) / 2, dialog.height() - cancel_button.height() - 3)
        start_button.move(dialog.width()/2, dialog.height() - start_button.height() - 3)
        cancel_button.show()
        start_button.show()

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

        self.gui.run.startRun(run_name)
        dialog.done(2)  # This 2 is arbitrary expect it differs from the the canceled

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

    @staticmethod  # Idk if this will stay static but for now
    def startRunCanceled(dialog):
        """
        Basically do nothing but close the dialog
        """
        dialog.done(1)  # This 1 is arbitrary

    def update(self):
        self.centralWidget.update()

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

        # Marker for if the controls area is being edited
        self.is_editing = False

        self.controlsWidget = ControlsWidget(self)
        self.controlsPanelWidget = ControlsPanelWidget(self)
        self.missionWidget = MissionWidget(self)

        # Some variables depend on the init of ControlsPanelWidget so has to happen after it inits
        self.controlsWidget.finalizeInit()

    @overrides
    def resizeEvent(self, e: QResizeEvent):
        """
        Called when window is re-sized, updates height and width vas

        :param e: variable holding event data
        """
        self.width = self.size().width()
        self.height = self.size().height()

