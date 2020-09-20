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

    def __init__(self, channels, cycle_time, num_channels=4, *args, **kwargs):
        super(DataViewer, self).__init__(*args, **kwargs)
        
        # load data channels
        self.channels = channels # list of channel names
        self.num_channels = num_channels # number of data channels in plot
        self.cycle_time = cycle_time # cycle time of application in ms
        self.default_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'] # stolen from matplotlib

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
        completer = QtWidgets.QCompleter(self.channels) # channel autocomplete
        self.config_layout = QtWidgets.QGridLayout()
        self.config_tab.setLayout(self.config_layout)
        self.switches = [] # L/R switches
        self.series = [] # channel inputs
        self.colors = [] # color selector
        self.curves = [] # pyqtgraph curve objects
        
        # plot title
        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("Plot Title")
        self.config_layout.addWidget(self.title_edit, 0, 1)
        font = self.title_edit.font()
        font.setPointSize(12)
        self.title_edit.setFont(font)
        self.title_edit.editingFinished.connect(self.titleUpdate)
        
        # setup channel rows
        for i in range(num_channels):
            self.switches.append(Switch())
            self.switches[i].clicked.connect(lambda state: self.redrawCurves())
            self.curves.append(pg.PlotCurveItem())
            self.config_layout.addWidget(self.switches[i], i+1, 0)
            dropdown = QtWidgets.QLineEdit()
            font = dropdown.font()
            font.setPointSize(12)
            dropdown.setFont(font)
            dropdown.setCompleter(completer)
            dropdown.editingFinished.connect(lambda: self.redrawCurves())
            self.series.append(dropdown)
            self.config_layout.addWidget(self.series[i], i+1, 1)
            self.colors.append(ColorButton(default_color=self.default_colors[i]))
            self.colors[i].colorChanged.connect(lambda: self.redrawCurves())
            self.config_layout.addWidget(self.colors[i], i+1, 2)
        
        # setup duration field
        self.duration_edit = QtWidgets.QLineEdit("30")
        self.duration_label = QtWidgets.QLabel("Seconds")
        self.config_layout.addWidget(self.duration_edit, num_channels+1, 0)
        self.config_layout.addWidget(self.duration_label, num_channels+1, 1)
        self.duration_edit.editingFinished.connect(self.durationUpdate)
        self.durationUpdate()

        # column sizing
        self.config_layout.setColumnStretch(0, 15)
        self.config_layout.setColumnStretch(1, 85)
        self.config_layout.setColumnStretch(2, 5)

        # setup 2 axis plot
        self.left = self.plot.plotItem
        self.left.addLegend()
        self.right = pg.ViewBox()
        self.left.showAxis('right')
        self.left.scene().addItem(self.right)
        self.left.getAxis('right').linkToView(self.right)
        self.right.setXLink(self.left)
        self.viewUpdate()
        self.left.vb.sigResized.connect(self.viewUpdate)
    
    def loadConfig(self, config):
        # viewer config load
        self.title_edit.setText(config[0])
        self.titleUpdate()
        self.duration_edit.setText(config[1])
        self.durationUpdate()
        for i in range(self.num_channels):
            curve_config = config[i+2]
            self.switches[i].setChecked(bool(curve_config[0]))
            self.series[i].setText(curve_config[1])
            self.colors[i].setColor(curve_config[2])
        self.redrawCurves()

    def saveConfig(self):
        # save config
        config = [self.title_edit.text(), self.duration_edit.text()]
        for i in range(self.num_channels):
            config.append([self.switches[i].isChecked(), self.series[i].text(), self.colors[i].color()])
        return config

    def printCurves(self):
        # debug function to dump children of plots
        print("right: " + str([dataobj for dataobj in self.right.allChildren()]))
        print("left: " + str([dataobj for dataobj in self.left.getViewBox().allChildren()]))
    
    def redrawCurves(self):
        # remove curves from legend
        self.left.legend.clear()

        for idx in range(self.num_channels):
            # remove curve from plot
            for dataobj in self.right.allChildren():
                if dataobj is self.curves[idx]:
                    self.right.removeItem(dataobj)
            
            for dataobj in self.left.getViewBox().allChildren():
                if dataobj is self.curves[idx]:
                    self.left.removeItem(dataobj)
            
            # handle lines
            parsed = self.series[idx].text().split("=") # parse
            if len(parsed[0]) > 0:
                if (parsed[0] == "line" and len(parsed) == 2):
                    self.curves[idx] = pg.InfiniteLine(pos=parsed[1], angle=0) # add infinite line
                else:
                    self.curves[idx] = pg.PlotCurveItem() # add standard curve
                    self.left.legend.addItem(self.curves[idx], parsed[0]) # add to legend
            
            # set curve color
            if self.colors[idx].color():
                self.curves[idx].setPen(pg.mkPen(QtGui.QColor(self.colors[idx].color())))
            
            # set curve to left or right side
            if self.switches[idx].isChecked():
                self.right.addItem(self.curves[idx])
            else:
                self.left.addItem(self.curves[idx])

    def viewUpdate(self):
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
        # update plot title
        self.plot.setTitle(self.title_edit.text())
    
    def durationUpdate(self):
        # update duration on edit
        self.duration = int(self.duration_edit.text())

    def update(self, frame):
        # update dataviewer with new data
        points = int(self.duration*1000/self.cycle_time)
        data = frame.tail(points)
        for i in range(self.num_channels):
            # get channel name
            channel_name = self.series[i].text()
            if channel_name in self.channels:
                self.curves[i].setData(x=data["time"].to_numpy(), y=data[channel_name].to_numpy())
        

if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    plot = DataViewer([], 250, num_channels=4)
    plot.show()
    sys.exit(app.exec())