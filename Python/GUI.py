import sys
import os
import json

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from baseGUI import BaseGui
from controlsWindow import ControlsWindow

from plotWindow import PlotWindow

from configurationManager import ConfigurationManager

from campaign import Campaign

"""
Program start point. This class handles all child windows of the gui
"""


class GUI(BaseGui):  # Inherits QObject just so signals can be used

    def __init__(self, qapp: QApplication):
        super().__init__(qapp)  # This calls above BaseGui __init__

        # This variable holds the current Run class that is being used to conduct the test
        self.campaign = Campaign(self)
        #self.configuration = ConfigurationManager(self)

        # If in debug mode the gui overrides the command sending and instead shows what would happen if successful
        self.debug_mode = False

        #  self.plotWindow = PlotWindow()
        self.controlsWindow = ControlsWindow(self)
        self.setMainWindow(self.controlsWindow)

        self.setStatusBarMessage("GUI startup")

    def postInit(self):
        """
        Function for doing some things that can't be done in init
        """
        self.controlsWindow.postInit()

    @pyqtSlot()
    def gotConnectionToServer(self):
        """
        Function that is called when the connection to the server is gotten
        :return: None
        """
        super().gotConnectionToServer()
        # When new connection, check if in campaign or not. If not then enable campaign to be started, otherwise send a
        # a command to restart old campaign
        if not self.campaign.is_active:
            self.controlsWindow.startRunAct.setEnabled(True)
        else:
            self.liveDataHandler.sendCommand(6, [str(self.campaign.saveName)])
            self.controlsWindow.centralWidget.controlsSidebarWidget.tabWidget.noteWidget.enableNoteCreation()

    @pyqtSlot()
    def serverDisconnect(self):
        """
        Function that is called when server is disconnected, either by the user or because of a server quit/ crash
        :return: None
        """
        super().serverDisconnect()
        self.controlsWindow.startRunAct.setDisabled(True)
        self.controlsWindow.centralWidget.controlsSidebarWidget.tabWidget.noteWidget.disableNoteCreation(True)


if __name__ == '__main__':

    currentExitCode = GUI.EXIT_CODE_REBOOT
    while currentExitCode == GUI.EXIT_CODE_REBOOT:

        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        app = QApplication(sys.argv)
        app.setApplicationName("MASA GUI")
        app.setApplicationDisplayName("MASA GUI")

        app.setWindowIcon(QIcon('Images/M_icon.png'))
        gui = GUI(app)

        QTimer.singleShot(100, gui.postInit)  # Need to call this after exec_ for proper screen placement
        currentExitCode = app.exec_()
        gui.savePreferences()
        app = None