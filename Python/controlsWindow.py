from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from controlsWidget import ControlsWidget
from controlsPanelWidget import ControlsPanelWidget

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
        self.w = ControlsCentralWidget(self.gui, self)
        self.setCentralWidget(self.w)
        self.fileName = ""

        self.setWindowTitle(self.title)
        self.setGeometry(self.w.left, self.w.top, self.w.width, self.w.height)

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

        # EDIT -> Enter Edit Mode
        enterEditAct = QAction('&Enter Edit Mode', self)
        enterEditAct.setShortcut('Ctrl+E')
        enterEditAct.triggered.connect(self.enterEdit)

        # EDIT -> Leave Edit Mode
        exitEditAct = QAction('&Leave Edit Mode', self)
        exitEditAct.setShortcut('Ctrl+Shift+E')
        exitEditAct.triggered.connect(self.exitEdit)

        # Creates menu bar, adds tabs file, edit, view
        menuBar = self.menuBar()
        menuBar.setNativeMenuBar(True)
        file_menu = menuBar.addMenu('File')
        edit_menu = menuBar.addMenu('Edit')
        view_menu = menuBar.addMenu('View')

        # Adds all the file buttons to the file tab
        file_menu.addAction(newAct)
        file_menu.addAction(openAct)
        file_menu.addAction(saveAct)
        file_menu.addAction(saveAsAct)
        file_menu.addAction(exitAct)

        # Adds all the edit button to the edit tab
        edit_menu.addAction(enterEditAct)
        edit_menu.addAction(exitEditAct)

        # Add all menus to a dict for easy access by other functions
        self.menus = {"File": file_menu,
                      "Edit": edit_menu,
                      "View": view_menu}
        
        self.showMaximized()

    def saveRegular(self):
        """
        Executes the save action. If file is named, just runs saveData.
        If file is not yet named, executes Save As action.
        """
        if self.fileName != "":
            self.w.controlsWidget.saveData(self.fileName)
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
            self.w.controlsWidget.saveData(fileName)

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
            self.w.controlsWidget.loadData(fileName)

    def newFile(self):
        """
        Creates new blank untitled file. Basically just erases everything and sets filename to unset
        """
        self.fileName = ""
        length = len(self.w.controlsWidget.object_list)
        for i in range(length):
            print(self.w.controlsWidget.object_list[0].short_name)
            self.w.controlsWidget.deleteObject(self.w.controlsWidget.object_list[0])

        self.w.controlsWidget.tube_list = []

    def enterEdit(self):
        """
        If not already editing, calls toggle edit to enter edit mode
        """
        if not self.w.is_editing:
            self.w.controlsWidget.toggleEdit()

    def exitEdit(self):
        """
        Same as enter edit mode, but the opposite
        """
        if self.w.is_editing:
            self.w.controlsWidget.toggleEdit()

class ControlsCentralWidget(QWidget):
    """
    Window to house the controls and editing Widgets
    """

    def __init__(self, parent=None, window=None):
        super().__init__()
        self.parent = parent
        self.gui = self.parent
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

