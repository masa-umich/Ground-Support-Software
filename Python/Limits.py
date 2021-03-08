from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import sys
import os
import ctypes
from s2Interface import S2_Interface
from LedIndicatorWidget import LedIndicator
from ClientWidget import ClientWidget, ClientDialog
import random
import json

class Limit(QtWidgets.QGroupBox):
    def __init__(self, channels, parent = None, *args, **kwargs):
        super(Limit, self).__init__(*args, **kwargs)
        
        self.parent = parent
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
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

        self.delete_button = QtWidgets.QPushButton("x")
        #self.delete_button.setStyleSheet("")
        self.layout.addWidget(self.delete_button, 0, 5)
        self.delete_button.clicked.connect(self.delete)
        #self.delete_button.setIcon(QtGui.QIcon('Python/xicon.jpg'))
        self.delete_button.setFixedSize(QtCore.QSize(30,30))

        self.layout.setColumnStretch(0, 2)
        self.layout.setColumnStretch(1, 10)
        self.layout.setColumnStretch(2, 10)
        self.layout.setColumnStretch(3, 10)
        self.layout.setColumnStretch(4, 20)
        self.layout.setColumnStretch(5, 1)

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
        self.channel.setText(str(config["channel"]))
        self.low.setText(str(config["low"]))
        self.high.setText(str(config["high"]))

    def save(self):
        return {"channel": self.channel.text(), "low": self.low.text(), "high": self.high.text()}

    def delete(self):
        self.parent.delete_limit(self)
    

class LimitWidget(QtWidgets.QWidget):
    def __init__(self, num_channels, *args, **kwargs):
        super(LimitWidget, self).__init__(*args, **kwargs)
        
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.setStyleSheet("")

        self.interface = S2_Interface()
        self.channels = self.interface.channels
        self.num_channels = num_channels

        self.limits_box = QtWidgets.QWidget()
        self.limits_layout = QtWidgets.QVBoxLayout()
        self.limits_box.setLayout(self.limits_layout)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.limits_box)
        self.layout.addWidget(self.scroll, 0, 0, 1, 2)

        self.limits = []
        for i in range(num_channels):
            self.limits.append(Limit(self.channels, parent=self))
            self.limits_layout.addWidget(self.limits[i])

        self.add_limit_button = QtWidgets.QPushButton("+")
        self.limits_layout.addWidget(self.add_limit_button)
        self.add_limit_button.clicked.connect(self.add_limit)
        self.limits_layout.addStretch(1)

        self.load_button = QtWidgets.QPushButton("Load")
        self.layout.addWidget(self.load_button, 2, 1, 1, 1)
        self.load_button.clicked.connect(self.load)
        self.save_button = QtWidgets.QPushButton("Save")
        self.layout.addWidget(self.save_button, 2, 0, 1, 1)
        self.save_button.clicked.connect(self.save)
    
    def delete_limit(self, widget):
        for i in range(len(self.limits)):
            if self.limits[i] is widget:
                self.limits_layout.removeWidget(widget)
                widget.deleteLater()
                self.limits.pop(i)
                break
        self.num_channels = len(self.limits)
        
    def add_limit(self):
        self.limits.append(Limit(self.channels, parent=self))
        self.limits_layout.insertWidget(self.num_channels, self.limits[-1])
        self.num_channels = len(self.limits)
    
    def save(self):
        configs = {"num_channels": self.num_channels, "limit_configs": [limit.save() for limit in self.limits]}
        savename = QtGui.QFileDialog.getSaveFileName(self, 'Save Config', 'limits.cfg', "Config (*.cfg)")[0]
        with open(savename, "w") as f:
            json.dump(configs, f)
            
    def load(self):
        loadname = QtGui.QFileDialog.getOpenFileName(self, "Load Config", "", "Config (*.cfg)")[0]
        with open(loadname, "r") as f:
            configs = json.load(f)
        while self.num_channels < int(configs["num_channels"]):
            self.add_limit()
        for i in range(len(self.limits)):
            self.limits[i].load(configs["limit_configs"][i])

    def update(self):
        for i in range(len(self.limits)):
            channel = self.limits[i].channel.text()
            if channel in self.channels:
                #limits[i].update(dataframe[channel])
                self.limits[i].update(random.randrange(-100, 100)) # fake data for testing

class LimitDialog(QtWidgets.QDialog):
    def __init__(self, num_channels, *args, **kwargs):
        super(LimitDialog, self).__init__(*args, **kwargs)
        self.widget = LimitWidget(num_channels, *args, **kwargs)
        self.setModal(False)
        self.setWindowTitle("Limits")
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.widget)
        self.setLayout(self.layout)

if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    
    # initialize application
    appid = 'MASA.DataViewer' # arbitrary string
    if os.name == 'nt': # Bypass command because it is not supported on Linux 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    else:
        pass
        # NOTE: On Ubuntu 18.04 this does not need to done to display logo in task bar
    app.setWindowIcon(QtGui.QIcon('Images/logo_server.png'))

    #app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    limit = LimitDialog(12)
    
    #timer and tick updates
    cycle_time = 100 # in ms
    timer = QtCore.QTimer()
    timer.timeout.connect(limit.widget.update)
    timer.start(cycle_time)

    limit.show()
    sys.exit(app.exec())
