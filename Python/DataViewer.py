from PyQt5 import QtGui, QtCore, QtWidgets
#from PyQt5.QtCore import Qt, QRect
import pyqtgraph as pg
import sys
from Switch import Switch
import pandas as pd

class DataViewer(QtWidgets.QTabWidget):
    """
    Custom QtWidget to plot data
    """

    def __init__(self, channels, num_channels=4, *args, **kwargs):
        super(DataViewer, self).__init__(*args, **kwargs)

        self.channels = channels

        # initialize tabs
        self.config_tab = QtWidgets.QWidget()
        self.plot_tab = pg.GraphicsLayoutWidget()
        self.addTab(self.config_tab, "Config")
        self.addTab(self.plot_tab, "Plot")

        # set up config
        completer = QtWidgets.QCompleter(self.channels)
        self.config_layout = QtWidgets.QGridLayout()
        self.config_tab.setLayout(self.config_layout)
        self.switches = []
        self.series = []
        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("Plot Title")
        #self.title_label = QtWidgets.QLabel("Plot Title")
        self.config_layout.addWidget(self.title_edit, 0, 1)
        font = self.title_edit.font()
        font.setPointSize(12)
        self.title_edit.setFont(font)
        self.title_edit.editingFinished.connect(self.titleUpdate)
        #self.config_layout.addWidget(self.title_label, 0, 0)
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
        self.config_layout.setColumnStretch(0, 15)
        self.config_layout.setColumnStretch(1, 85)

        # setup plot
        self.plot_tab.setBackground('w')
        self.plot = pg.PlotItem()
        self.plot_tab.addItem(self.plot)

    def getActive(self):
        # returns list of active channels
        return [str(s.text()) for s in self.series if str(s.text()) is not ""]

    def isActive(self):
        # returns True if plot is configured with a channel
        return len(self.getActive())>0

    def titleUpdate(self):
        self.plot.setTitle(self.title_edit.text())

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