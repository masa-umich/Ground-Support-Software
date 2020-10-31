import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from controlsWindow import ControlsWindow
from constants import  Constants



"""
Program start point. This class handles all child windows of the gui
"""
class GUI:
    def __init__(self):
        # Get the screen resolution of the user
        self.screenResolution = [app.desktop().screenGeometry().width(),app.desktop().screenGeometry().height()]
        # Get the scaling ratio for objects in the gui. The scale ratio would be 1 on a screen of a resolution of 1600
        # wide and 1200 tall
        self.pixel_scale_ratio = [self.screenResolution[0] / 1600, self.screenResolution[1]/1200]

        if sys.platform == "win32":
            self.platform = "Windows"
        elif sys.platform == "darwin":
            self.platform = "OSX"

        # Put all the setup for platform specific things here
        if self.platform == "Windows":
            # Once again the font scale is 1 on Mac and smaller for windows. This should produce identical results
            self.font_scale_ratio = 0.82

            Constants.line_width = 2
        elif self.platform == "OSX":
            self.font_scale_ratio = 1

            Constants.line_width = 2
        #self.plotWindow = PlotWindow()
        self.controlsWindow = ControlsWindow(self)
    
    def update(self):
        self.controlsWindow.update()





if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    gui = GUI()

    #timer and tick updates
    cycle_time = 200 # in ms
    timer = QTimer()
    timer.timeout.connect(gui.update)
    timer.start(cycle_time)

    sys.exit(app.exec_())
