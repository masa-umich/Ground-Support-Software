from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QRect
import pyqtgraph as pg
import sys

#switch widget modified from https://stackoverflow.com/questions/56806987/switch-button-in-pyqt
class Switch(QtWidgets.QPushButton):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setMinimumWidth(82)
        self.setMinimumHeight(22)

    def paintEvent(self, event):
        label = "L" if self.isChecked() else "R"
        bg_color = Qt.darkGray

        radius = 15
        width = 40
        center = self.rect().center()

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.translate(center)
        painter.setBrush(Qt.lightGray)

        pen = QtGui.QPen(Qt.white)
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawRoundedRect(QRect(-width, -radius, 2*width, 2*radius), radius, radius)
        painter.setBrush(QtGui.QBrush(bg_color))
        sw_rect = QRect(-radius, -radius, width + radius, 2*radius)
        if not self.isChecked():
            sw_rect.moveLeft(-width)
        painter.drawRoundedRect(sw_rect, radius, radius)
        painter.drawText(sw_rect, Qt.AlignCenter, label)


class DataViewer(QtWidgets.QTabWidget):
    """
    Custom Qt Widget to plot data
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
        self.config_layout = QtWidgets.QGridLayout()
        self.config_tab.setLayout(self.config_layout)
        self.switches = []
        self.series = []
        for i in range(num_channels):
            self.switches.append(Switch())
            self.config_layout.addWidget(self.switches[i], i, 1)
            dropdown = QtWidgets.QComboBox()
            dropdown.clear()
            dropdown.addItem("")
            dropdown.addItems(self.channels)
            font = dropdown.font()
            font.setPointSize(12)
            dropdown.setFont(font)
            self.series.append(dropdown)
            self.config_layout.addWidget(self.series[i], i, 0)
        self.config_layout.setColumnStretch(0, 85)
        self.config_layout.setColumnStretch(1, 15)

        # setup plot
        self.plot_tab.setBackground('w')
        self.plot_tab.addPlot()

    def getActive(self):
        # returns list of active channels
        return [str(s.currentText()) for s in self.series if str(s.currentText()) is not ""]

    def isActive(self):
        # returns True if plot is configured with a channel
        return len(self.getActive())>0

    def update(self, frame):
        data = frame[self.getActive()]
        # pull out required data
        # push data to plot
        print(data.tail(500))
        

if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    plot = DataViewer()
    plot.show()
    app.exec()