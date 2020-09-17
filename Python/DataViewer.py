from PyQt5 import QtGui, QtCore, QtWidgets
#from PyQt5.QtCore import Qt, QRect
import pyqtgraph as pg
import sys
from Switch import Switch
from ColorButton import ColorButton
import pandas as pd

class DataViewer(QtWidgets.QTabWidget):
    """
    Custom QtWidget to plot data
    """

    def __init__(self, channels, num_channels=4, *args, **kwargs):
        super(DataViewer, self).__init__(*args, **kwargs)
        
        # load data channels
        self.channels = channels

        # initialize tabs
        self.config_tab = QtWidgets.QWidget()
        self.plot_tab = QtWidgets.QWidget()
        self.plot_layout = QtWidgets.QVBoxLayout()
        self.plot_layout.setContentsMargins(20, 20, 20, 20)
        self.plot_tab.setLayout(self.plot_layout)
        self.plot = pg.PlotWidget(background='w')
        self.plot_layout.addWidget(self.plot)
        self.addTab(self.config_tab, "Config")
        self.addTab(self.plot_tab, "Plot")

        # set up config
        completer = QtWidgets.QCompleter(self.channels)
        self.config_layout = QtWidgets.QGridLayout()
        self.config_tab.setLayout(self.config_layout)
        self.switches = []
        self.series = []
        self.colors = []
        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("Plot Title")
        self.config_layout.addWidget(self.title_edit, 0, 1)
        font = self.title_edit.font()
        font.setPointSize(12)
        self.title_edit.setFont(font)
        self.title_edit.editingFinished.connect(self.titleUpdate)
        for i in range(num_channels):
            self.switches.append(Switch())
            self.config_layout.addWidget(self.switches[i], i+1, 0)
            dropdown = QtWidgets.QLineEdit()
            font = dropdown.font()
            font.setPointSize(12)
            dropdown.setFont(font)
            dropdown.setCompleter(completer)
            self.series.append(dropdown)
            self.config_layout.addWidget(self.series[i], i+1, 1)
            self.colors.append(ColorButton())
            self.config_layout.addWidget(self.colors[i], i+1, 2)
        self.duration_edit = QtWidgets.QLineEdit("30")
        self.duration_label = QtWidgets.QLabel("Seconds")
        self.config_layout.addWidget(self.duration_edit, num_channels+1, 0)
        self.config_layout.addWidget(self.duration_label, num_channels+1, 1)
        self.duration_edit.editingFinished.connect(self.durationUpdate)
        self.config_layout.setColumnStretch(0, 15)
        self.config_layout.setColumnStretch(1, 85)
        self.config_layout.setColumnStretch(2, 5)

        # setup plot
        self.left = self.plot.plotItem
        self.right = pg.ViewBox()
        self.left.showAxis('right')
        self.left.scene().addItem(self.right)
        self.left.getAxis('right').linkToView(self.right)
        self.right.setXLink(self.left)
        self.updateViews()
        self.left.vb.sigResized.connect(self.updateViews)
    
    def updateViews(self):
        # resize plot on window resize
        self.right.setGeometry(self.left.vb.sceneBoundingRect())
        self.right.linkedViewChanged(self.left.vb, self.right.XAxis)

    def getActive(self):
        # returns list of active channels
        return [str(s.text()) for s in self.series if str(s.text()) is not ""]

    def isActive(self):
        # returns True if plot is configured with a channel
        return len(self.getActive())>0

    def titleUpdate(self):
        self.plot.setTitle(self.title_edit.text())
    
    def durationUpdate(self):
        self.duration = int(self.duration_edit.text)

    def update(self, frame):
        pass
        #self.plot.setTitle(self.title_edit.text())
        # data = frame[self.getActive()]
        # pull out required data
        # push data to plot
        # print(data.tail(500))
        

if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    plot = DataViewer([])
    plot.show()
    app.exec()