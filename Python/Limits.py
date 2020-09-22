from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import sys
from hotfire_packet import ECParse
from LedIndicatorWidget import LedIndicator
from ClientWidget import ClientWidget, ClientDialog
import random
import json

class Limit(QtWidgets.QGroupBox):
    def __init__(self, channels, *args, **kwargs):
        super(Limit, self).__init__(*args, **kwargs)
        
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.setStyleSheet("background-color: white;")
        self.setAutoFillBackground(True)

        # status indicator
        self.indicator = LedIndicator()
        self.indicator.off_color_1 = QtGui.QColor(255, 0, 0)
        self.indicator.off_color_2 = QtGui.QColor(176, 0, 0)
        self.indicator.setDisabled(True)
        self.layout.addWidget(self.indicator, 0, 0)
        
        # bounds and value
        self.low = QtWidgets.QLineEdit()
        self.low.setPlaceholderText("Low")
        self.value = QtWidgets.QLabel("Value")
        self.value.setFixedWidth(100)
        self.value.setAlignment(Qt.AlignCenter)
        self.high = QtWidgets.QLineEdit()
        self.high.setPlaceholderText("High")
        self.layout.addWidget(self.low, 0, 1)
        self.layout.addWidget(self.value, 0, 2)
        self.layout.addWidget(self.high, 0, 3)
        
        # channel selection
        self.channel = QtWidgets.QLineEdit()
        self.channel.setPlaceholderText("Channel")
        completer = QtWidgets.QCompleter(channels) # channel autocomplete
        self.channel.setCompleter(completer)
        self.layout.addWidget(self.channel, 0, 4)

        self.layout.setColumnStretch(0, 0.5)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)
        self.layout.setColumnStretch(3, 1)
        self.layout.setColumnStretch(4, 2)

    def update(self, val):
        val = float(val)
        self.value.setText(str(val))
        if len(self.high.text()) > 0 and len(self.low.text()) > 0:
            try:
                if val <= float(self.high.text()) and val >= float(self.low.text()):
                    self.indicator.setChecked(True)
                else:
                    self.indicator.setChecked(False)
            except:
                pass

    def load(self, config):
        self.channel = str(config["channel"])
        self.low = str(config["low"])
        self.high = str(config["high"])

    def save(self):
        return {"channel": self.channel.text(), "low": self.low.text(), "high": self.high.text()}

class LimitWidget(QtWidgets.QWidget):
    def __init__(self, num_channels, *args, **kwargs):
        super(LimitWidget, self).__init__(*args, **kwargs)
        
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.setStyleSheet("")

        self.parser = ECParse()
        self.channels = [item for item in self.parser.items if (item is not 'zero' and item is not '')]

        self.limits = []
        for i in range(num_channels):
            self.limits.append(Limit(self.channels))
            self.layout.addWidget(self.limits[i], i, 0, 1, 2)

        self.load_button = QtWidgets.QPushButton("Load")
        self.layout.addWidget(self.load_button, num_channels, 0, 1, 1)
        self.load_button.clicked.connect(self.load)
        self.save_button = QtWidgets.QPushButton("Save")
        self.layout.addWidget(self.save_button, num_channels, 1, 1, 1)
        self.save_button.clicked.connect(self.save)
    
    def save(self):
        configs = [limit.save() for limit in self.limits]
        savename = QtGui.QFileDialog.getSaveFileName(self, 'Save Config', 'dataviewer.cfg', "Config (*.cfg)")[0]
        with open(savename, "w") as f:
            json.dump(configs, f)
            
    def load(self):
        loadname = QtGui.QFileDialog.getOpenFileName(self, "Load Config", "", "Config (*.cfg)")[0]
        with open(loadname, "r") as f:
            configs = json.load(f)
        for i in range(len(self.limits)):
            self.limits[i].load(configs[i])

    def update(self):
        for i in range(len(self.limits)):
            channel = self.limits[i].channel.text()
            if channel in self.channels:
                #limits[i].update(dataframe[channel])
                self.limits[i].update(random.randrange(-100, 100))

if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    
    limit = LimitWidget(12)
    
    #timer and tick updates
    cycle_time = 100 # in ms
    timer = QtCore.QTimer()
    timer.timeout.connect(limit.update)
    timer.start(cycle_time)

    limit.show()
    sys.exit(app.exec())
