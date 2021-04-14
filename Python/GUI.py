import sys
import os
import json

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from controlsWindow import ControlsWindow
from constants import Constants

from configurationManager import ConfigurationManager

from run import Run

"""
Program start point. This class handles all child windows of the gui
"""


class GUI:

    EXIT_CODE_REBOOT = -52
    EXIT_CODE_NOMINAL = 0
    EXIT_CODE_ERROR = -1
    LAUNCH_DIRECTORY = "LaunchFiles/"

    def __init__(self):


        # Check which platform we are working with
        if sys.platform == "win32":
            self.platform = "Windows"
        elif sys.platform == "darwin":
            self.platform = "OSX"

        # Get the screen resolution of the user
        self.screenResolution = [app.desktop().screenGeometry().width(), app.desktop().screenGeometry().height()]

        # Check if the launch files exist, if so load preferences from there
        if os.path.isdir(GUI.LAUNCH_DIRECTORY):
            self.loadPreferences()

        # If this is the first time running, create required directories, and guess at scaling values
        else:
            # Ask user for workspace directory to search for configurations
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            self.workspace_path = str(QFileDialog.getExistingDirectory(None, "Select Workspace Directory", options=options))
            if self.workspace_path == "":
                sys.exit("No Workspace Path Provided")

            os.mkdir(path=self.workspace_path + "/Configurations/")
            os.mkdir(path=self.workspace_path + "/Run_Data/")

            os.mkdir(path=GUI.LAUNCH_DIRECTORY)
            readMe = open(GUI.LAUNCH_DIRECTORY+"README.txt", "x")
            readMe.write("This is the directory that the GUI pulls startup files from, do not delete, "
                         "it will come back.\n\nIf for some reason u want to reset this delete the whole folder")

            #Get the scaling ratio for objects. The scale ratio would be 1 on a screen of a resolution of 1600
            # wide and 1200 tall
            self.pixel_scale_ratio = [self.screenResolution[0] / 1600, self.screenResolution[1]/1200]

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

        # Add in fonts
        QFontDatabase.addApplicationFont("Fonts/Montserrat/Montserrat-Medium.ttf")
        QFontDatabase.addApplicationFont("Fonts/RobotoMono/RobotoMono-Regular.ttf")
        QFontDatabase.addApplicationFont("Fonts/RobotoMono/RobotoMono-Light.ttf")
        QFontDatabase.addApplicationFont("Fonts/RobotoMono/RobotoMono-Medium.ttf")
        QFontDatabase.addApplicationFont("Fonts/RobotoMono/RobotoMono-Thin.ttf")
        QFontDatabase.addApplicationFont("Fonts/RobotoMono/RobotoMono-Italic.ttf")

        # This variable holds the current Run class that is being used to conduct the test
        self.run = Run()
        #self.configuration = ConfigurationManager(self)

        # If in debug mode the gui overrides the command sending and instead shows what would happen if successful
        self.debug_mode = False

        #self.plotWindow = PlotWindow()
        self.controlsWindow = ControlsWindow(self)

        self.controlsWindow.statusBar().showMessage("GUI startup")
        
        # set client path for run class (for server checkpointing)
        self.run.setClient(self.controlsWindow.client_dialog.client)
    
    def update(self):
        self.controlsWindow.update()

    def savePreferences(self):

        # Generate dict of preferences to save
        preferences = {
            "workspace_path": self.workspace_path,
            "pixel_scale_ratio": {"x":self.pixel_scale_ratio[0], "y":self.pixel_scale_ratio[1]},
            "font_scale_ratio": self.font_scale_ratio,
            "line_width": Constants.line_width
        }

        # If file exits, open it and write over, if it does not, create and write
        if os.path.isfile(GUI.LAUNCH_DIRECTORY + "prefs.json"):
            pref_file = open(GUI.LAUNCH_DIRECTORY+"prefs.json", 'w')
        else:
            pref_file = open(GUI.LAUNCH_DIRECTORY + "prefs.json", "x")

        # Write the file
        json.dump(preferences, pref_file, indent="\t")

        pref_file.close()

        print("Preferences Saved")

    def loadPreferences(self):

        # Open and read the loaded json file
        with open(GUI.LAUNCH_DIRECTORY+"prefs.json", "r") as read_file:
            prefs = json.load(read_file)

        self.pixel_scale_ratio = [prefs["pixel_scale_ratio"]["x"], prefs["pixel_scale_ratio"]["y"]]
        self.font_scale_ratio = prefs["font_scale_ratio"]
        self.workspace_path = prefs["workspace_path"]
        Constants.line_width = prefs["line_width"]

        if not os.path.isdir(self.workspace_path):
            # Ask user for workspace directory to search for configurations
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            self.workspace_path = str(QFileDialog.getExistingDirectory(None, "Workspace not found: Select Workspace Directory", options=options))
            if self.workspace_path == "":
                sys.exit("No Workspace Path Provided")

if __name__ == '__main__':

    currentExitCode = GUI.EXIT_CODE_REBOOT
    while currentExitCode == GUI.EXIT_CODE_REBOOT:

        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        app = QApplication(sys.argv)
        print(QT_VERSION_STR)
        app.setStyle("Fusion")


        darkPalette = QPalette()
        darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
        darkPalette.setColor(QPalette.WindowText, Qt.white)
        darkPalette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
        darkPalette.setColor(QPalette.Base, QColor(42, 42, 42))
        darkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
        darkPalette.setColor(QPalette.ToolTipBase, Qt.white)
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

        app.setPalette(darkPalette)


        app.setWindowIcon(QIcon('Images/M_icon.png'))
        gui = GUI()

        #timer and tick updates
        cycle_time = 200 # in ms
        timer = QTimer()
        timer.timeout.connect(gui.update)
        timer.start(cycle_time)
        currentExitCode = app.exec_()
        #print(currentExitCode)
        gui.savePreferences()
        app = None