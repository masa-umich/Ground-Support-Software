import sys
import os
import json

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import webbrowser
from constants import Constants
from liveDataHandler import LiveDataHandler

from plotWindow import PlotWindow

from configurationManager import ConfigurationManager


class BaseGui(QObject):
    """
    Base GUI Ahh
    """

    EXIT_CODE_REBOOT = -52
    EXIT_CODE_NOMINAL = 0
    EXIT_CODE_ERROR = -1
    LAUNCH_DIRECTORY = "LaunchFiles/"

    guiExitSignal = pyqtSignal()

    def __init__(self, qapp : QApplication, mainWindow: QWindow = None):
        super().__init__()

        print("MASA GUI Version: " + Constants.GUI_VERSION)
        print("Python Version: " + str(sys.version_info))
        print("QT Version: " + QT_VERSION_STR)

        self.applyDarkTheme(qapp)

        # Check which platform we are working with
        if sys.platform == "win32":
            self.platform = "Windows"
        elif sys.platform == "darwin":
            self.platform = "OSX"

        # Get the screen resolution of the user
        if self.platform == "Windows":
            self.screenResolution = [qapp.desktop().screenGeometry().width(), qapp.desktop().availableGeometry().height()]
        else:
            # This includes the height of the app bar on mac
            self.screenResolution = [qapp.desktop().screenGeometry().width(), qapp.desktop().screenGeometry().height()]

        # Check if the launch files exist, if so load preferences from there
        if os.path.isdir(BaseGui.LAUNCH_DIRECTORY):
            self.loadPreferences()
        # If this is the first time running, create required directories, and guess at scaling values
        else:
            # Ask user for workspace directory to search for configurations
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            self.workspace_path = str(
                QFileDialog.getExistingDirectory(None, "Select Workspace Directory", options=options))
            if self.workspace_path == "":
                sys.exit("No Workspace Path Provided")

            os.mkdir(path=self.workspace_path + "/Configurations/")
            os.mkdir(path=self.workspace_path + "/Run_Data/")

            os.mkdir(path=BaseGui.LAUNCH_DIRECTORY)
            readMe = open(BaseGui.LAUNCH_DIRECTORY + "README.txt", "x")
            readMe.write("This is the directory that the GUI pulls startup files from, do not delete, "
                         "it will come back.\n\nIf for some reason u want to reset this delete the whole folder")

            # Get the scaling ratio for objects. The scale ratio would be 1 on a screen of a resolution of 1600
            # wide and 1200 tall
            self.pixel_scale_ratio = [self.screenResolution[0] / 1600, self.screenResolution[1] / 1200]

            # Put all the setup for platform specific things here
            if self.platform == "Windows":
                # Once again the font scale is 1 on Mac and smaller for windows. This should produce identical results
                self.font_scale_ratio = 0.82

                Constants.line_width = 2
            elif self.platform == "OSX":
                self.font_scale_ratio = 1

                Constants.line_width = 2

            # Write the save file
            self.savePreferences()

        print("Launch Directory: " + os.path.abspath(self.LAUNCH_DIRECTORY))
        print("Workspace Path: " + self.workspace_path)

        # Add in fonts
        QFontDatabase.addApplicationFont("Fonts/Montserrat/Montserrat-Medium.ttf")
        QFontDatabase.addApplicationFont("Fonts/RobotoMono/RobotoMono-Regular.ttf")
        QFontDatabase.addApplicationFont("Fonts/RobotoMono/RobotoMono-Light.ttf")
        QFontDatabase.addApplicationFont("Fonts/RobotoMono/RobotoMono-Medium.ttf")
        QFontDatabase.addApplicationFont("Fonts/RobotoMono/RobotoMono-Thin.ttf")
        QFontDatabase.addApplicationFont("Fonts/RobotoMono/RobotoMono-Italic.ttf")

        # This is a handler for the Client, which receives data and sends commands
        self.liveDataHandler = LiveDataHandler(self)
        self.liveDataHandler.getClient().gotConnectionToServerSignal.connect(self.gotConnectionToServer)
        self.liveDataHandler.getClient().serverDisconnectSignal.connect(self.serverDisconnect)

        self._mainWindow = mainWindow

    def setMainWindow(self, mainWindow: QMainWindow):
        """
        All GUI applications created with BaseGUI class need to call this function to allow the window to actually be
        displayed. This also does a couple simple things like add a status bar and a help menu
        :param mainWindow: main window of the application
        :return: None
        """
        self._mainWindow = mainWindow
        self._mainWindow.statusBar().setFixedHeight(22 * self.pixel_scale_ratio[1])

        self._mainWindow.setWindowTitle(self._mainWindow.windowTitle() + " (" + Constants.GUI_VERSION + ")")

        # Adds in help menu
        menuBar = self._mainWindow.menuBar()

        # Help -> Help Info
        helpAct = QAction("&Documentation", self)
        helpAct.triggered.connect(self.openWiki)

        # Help -> Report Issue
        reportIssueAct = QAction('&Report Issue', self)
        reportIssueAct.triggered.connect(self.reportIssue)

        help_menu = menuBar.addMenu('Help')
        help_menu.addAction(helpAct)
        help_menu.addAction(reportIssueAct)

        self.setStatusBarMessage("Lightweight Gui Startup")

    @staticmethod
    def reportIssue():
        """
            Opens a link to the gitlab issue ticket form so people can quickly fill out
        """
        webbrowser.open('https://gitlab.eecs.umich.edu/masa/avionics/gui/-/issues/new?issue%5Bmilestone_id%5D=')

    @staticmethod
    def openWiki():
        """
            Opens a link to the gitlab wiki
        """
        webbrowser.open('https://gitlab.eecs.umich.edu/masa/avionics/gui/-/wikis/GUI-Main-Page')

    @pyqtSlot()
    def gotConnectionToServer(self):
        """
        Function that is called when the connection to the server is gotten. Nothing to do by default
        :return: None
        """
        pass

    @pyqtSlot()
    def serverDisconnect(self):
        """
        Function that is called when server is disconnected, either by the user or because of a server quit/ crash
        Nothing to do by default
        :return: None
        """
        pass

    def savePreferences(self):

        # Generate dict of preferences to save
        preferences = {
            "workspace_path": self.workspace_path,
            "pixel_scale_ratio": {"x": self.pixel_scale_ratio[0], "y": self.pixel_scale_ratio[1]},
            "font_scale_ratio": self.font_scale_ratio,
            "line_width": Constants.line_width
        }

        # If file exits, open it and write over, if it does not, create and write
        if os.path.isfile(BaseGui.LAUNCH_DIRECTORY + "prefs.json"):
            pref_file = open(BaseGui.LAUNCH_DIRECTORY + "prefs.json", 'w')
        else:
            pref_file = open(BaseGui.LAUNCH_DIRECTORY + "prefs.json", "x")

        # Write the file
        json.dump(preferences, pref_file, indent="\t")

        pref_file.close()

        print("Preferences Saved")

    def loadPreferences(self):

        # Open and read the loaded json file
        with open(BaseGui.LAUNCH_DIRECTORY + "prefs.json", "r") as read_file:
            prefs = json.load(read_file)

        self.pixel_scale_ratio = [prefs["pixel_scale_ratio"]["x"], prefs["pixel_scale_ratio"]["y"]]
        self.font_scale_ratio = prefs["font_scale_ratio"]
        self.workspace_path = prefs["workspace_path"]
        Constants.line_width = prefs["line_width"]

        if not os.path.isdir(self.workspace_path):
            # Ask user for workspace directory to search for configurations
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            self.workspace_path = str(
                QFileDialog.getExistingDirectory(None, "Workspace not found: Select Workspace Directory",
                                                 options=options))
            if self.workspace_path == "":
                sys.exit("No Workspace Path Provided")

    def setStatusBarMessage(self, text: str, error: bool = False):
        """
        Set text and possible show as error for status bar
        :param text: text to set
        :param error: bool, true for error
        :return: none
        """
        if error:
            self._mainWindow.statusBar().setStyleSheet("background-color: red")
        else:
            self._mainWindow.statusBar().setStyleSheet("border-top :1px solid #4F4F52")

        self._mainWindow.statusBar().showMessage(text)

    @staticmethod
    def show_window(window: QWidget):
        """
        Shows a window or brings it to the front if already open.
        :param window: window to show (normally a dialog)
        :return:
        """

        if hasattr(window, 'getDialog'):
            window = window.getDialog()

        # open window
        window.show()

        # bring to front
        window.setWindowState(window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        window.raise_()
        window.activateWindow()

    def guiExit(self):
        """
        Called from window class when the main window is closed. Also when application is quit
        :return: none
        """
        # Let everyone know we about to shut down
        self.guiExitSignal.emit()

        # Let the client get out its last messages
        if self.liveDataHandler.getClient() is not None:
            self.liveDataHandler.getClient().sendAllCommands()
            self.liveDataHandler.getClient().disconnect()

        QCoreApplication.exit(self.EXIT_CODE_NOMINAL)

    def applyDarkTheme(self, qapp: QApplication):
        qapp.setStyle("Fusion")

        darkPalette = QPalette()
        darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
        darkPalette.setColor(QPalette.WindowText, Qt.white)
        darkPalette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
        darkPalette.setColor(QPalette.Base, QColor(42, 42, 42))
        darkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
        darkPalette.setColor(QPalette.ToolTipBase, Qt.black)
        darkPalette.setColor(QPalette.ToolTipText, Qt.white)
        darkPalette.setColor(QPalette.Text, Qt.white)
        darkPalette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
        darkPalette.setColor(QPalette.Dark, QColor(35, 35, 35))
        darkPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
        darkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
        darkPalette.setColor(QPalette.ButtonText, Qt.white)
        darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
        darkPalette.setColor(QPalette.BrightText, Qt.red)
        darkPalette.setColor(QPalette.Link, QColor(42, 130, 218))
        darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        darkPalette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
        darkPalette.setColor(QPalette.HighlightedText, Qt.white)
        darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))

        qapp.setPalette(darkPalette)