import sys

from controlsWindow import ControlsWindow
from liveVideoWindow import LiveVideoWindow

from PyQt5.QtWidgets import *


"""
Program start point. This class handles all child windows of the gui
"""
class GUI:

    def __init__(self):

        self.screenResolution = [app.desktop().screenGeometry().width(),app.desktop().screenGeometry().height()]

        #self.plotWindow = PlotWindow()
        self.controlsWindow = ControlsWindow(self)
        self.liveVideoWindow = LiveVideoWindow(self)





if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())
