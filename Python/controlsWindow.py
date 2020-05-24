from PyQt5.QtWidgets import *
from controlsWidget import ControlsWidget
from controlsPanelWidget import ControlsPanelWidget

"""
This file contains the class to create the main window
"""

class ControlsWindow(QMainWindow):
    """
    Window to house the controlsWidget
    """

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.gui = self.parent

        # Set geometry
        self.title = 'Controls Window'

        # Below numbers are arbitrary
        # TODO: Make them not arbitrary
        self.left = 0
        self.top = 0
        self.width = self.gui.screenResolution[0]
        self.height = self.gui.screenResolution[1]

        self.setWindowTitle(self.title)
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

        self.showMaximized()

        self.show()

        # Menu shit that is not ready yet
        # exitAct = QAction('&Save', self)
        # exitAct.setStatusTip('Exit application')
        # exitAct.triggered.connect(qApp.quit)
        #
        # self.statusBar()
        # self.statusBar().showMessage('Ready')
        #
        # menubar = self.menuBar()
        # fileMenu = menubar.addMenu('&File')
        # fileMenu.addAction(exitAct)
