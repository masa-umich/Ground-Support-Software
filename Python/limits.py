import sys
import os
import ctypes
import random
import json
from datetime import datetime

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import pandas as pd

from baseGUI import BaseGui
from s2Interface import S2_Interface
from LedIndicatorWidget import LedIndicator
from ClientWidget import ClientWidget, ClientDialog


class Limit(QtWidgets.QGroupBox):
    def __init__(self, channels: list, parent=None, *args, **kwargs):
        super(Limit, self).__init__(*args, **kwargs)

        self.parent = parent
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        # p = self.palette()
        # p.setColor(self.backgroundRole(), Qt.white)
        # self.setPalette(p)
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
        self.low.setFixedWidth(100)

        self.lower_bound_label = QtWidgets.QLabel("Lower Bound")
        self.lower_bound_label.setFixedWidth(100)
        self.lower_bound_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.lower_bound = QtWidgets.QComboBox(self)
        self.lower_bound.addItems(["min","<", "≤"])
        self.lower_bound.resize(self.lower_bound.sizeHint())
        # add signal stuff

        self.value = QtWidgets.QLabel("Value")
        self.value.setFixedWidth(100)
        self.value.setAlignment(Qt.AlignCenter)

        self.upper_bound_label = QtWidgets.QLabel("Upper Bound")
        self.upper_bound_label.setFixedWidth(80)
        self.upper_bound_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.upper_bound = QtWidgets.QComboBox(self)
        self.upper_bound.addItems(["max","<", "≤"])
        self.upper_bound.resize(self.upper_bound.sizeHint())
        # add signal stuff

        self.high = QtWidgets.QLineEdit()
        self.high.setPlaceholderText("High")
        self.high.setFixedWidth(100)

        self.layout.addWidget(self.low, 0, 1)
        self.layout.addWidget(self.lower_bound_label, 0, 2)
        self.layout.addWidget(self.lower_bound, 0, 3)
        self.layout.addWidget(self.value, 0, 4)
        self.layout.addWidget(self.upper_bound_label, 0, 5)
        self.layout.addWidget(self.upper_bound, 0, 6)
        self.layout.addWidget(self.high, 0, 7)

        # channel selection
        self.channel = QtWidgets.QLineEdit()
        self.channel.setPlaceholderText("Channel")
        completer = QtWidgets.QCompleter(channels)  # channel autocomplete
        self.channel.setCompleter(completer)
        self.channel.setFixedWidth(100)
        self.layout.addWidget(self.channel, 0, 8)

        self.delete_button = QtWidgets.QPushButton("x")
        # self.delete_button.setStyleSheet("")
        self.layout.addWidget(self.delete_button, 0, 9)
        self.delete_button.clicked.connect(self.delete)
        # self.delete_button.setIcon(QtGui.QIcon('Python/xicon.jpg'))
        self.delete_button.setFixedSize(QtCore.QSize(30, 30))

        self.layout.setColumnStretch(0, 2)
        self.layout.setColumnStretch(1, 10)
        self.layout.setColumnStretch(2, 10)
        self.layout.setColumnStretch(3, 10)
        self.layout.setColumnStretch(4, 20)
        self.layout.setColumnStretch(5, 1)

    def update(self, val: float):
        val = float(val)
        self.value.setText(str(val))
        if len(self.high.text()) > 0 and len(self.low.text()) > 0:
            try:
                if (self.lower_bound.currentText() == "<" and val > float(self.low.text()) or \
                    self.lower_bound.currentText() == "≤" and val >= float(self.low.text()) or \
                    self.lower_bound.currentText() == "min") and (self.upper_bound.currentText() == "<" \
                    and val < float(self.high.text()) or self.upper_bound.currentText() == "≤" and \
                    val <= float(self.high.text()) or self.upper_bound.currentText() == "max"):
                    self.indicator.setChecked(True)
                else:
                    self.indicator.setChecked(False)
            except:
                pass

    def load(self, config: dict):
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
        self.setMinimumWidth(850)

        self.interface = S2_Interface()
        self.channels = self.interface.channels
        self.num_channels = num_channels
        #self.client_dialog = client

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
    
        self.starttime = datetime.now().timestamp()

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
        configs = {"num_channels": self.num_channels,
                   "limit_configs": [limit.save() for limit in self.limits]}
        savename = QtGui.QFileDialog.getSaveFileName(
            self, 'Save Config', 'limits.cfg', "Config (*.cfg)")[0]
        with open(savename, "w") as f:
            json.dump(configs, f)

    def load(self):
        loadname = QtGui.QFileDialog.getOpenFileName(
            self, "Load Config", "", "Config (*.cfg)")[0]
        with open(loadname, "r") as f:
            configs = json.load(f)
        while self.num_channels < int(configs["num_channels"]):
            self.add_limit()
        for i in range(len(self.limits)):
            self.limits[i].load(configs["limit_configs"][i])

    def update_limits(self, last_packet: dict):
        if last_packet:
            last_packet["time"] -= self.starttime  # time to elapsed
            for i in range(len(self.limits)):
                channel = self.limits[i].channel.text()
                if channel in self.channels:
                    self.limits[i].update(last_packet[channel])
    
    # def cycle(self):
    #     last_packet = self.client_dialog.client.cycle()
    #     self.update_limits(last_packet)


class LimitWindow(QtWidgets.QMainWindow):
    def __init__(self, num_channels, gui, singular : bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.gui = gui
        # menu bar
        self.main_menu = self.menuBar()
        self.main_menu.setNativeMenuBar(True)
        self.options_menu = self.main_menu.addMenu('&Options')

        # # set up client
        # if client is None:
        #     self.client_dialog = ClientDialog(None)
        #     # connection menu item

        if singular:
            self.connect = QtGui.QAction("&Connection", self.options_menu)
            self.connect.setShortcut('Alt+C')
            self.connect.triggered.connect(lambda: self.gui.show_window(self.gui.liveDataHandler.getClient()))
            self.options_menu.addAction(self.connect)
        # else:
        #     self.client_dialog = client

        self.gui.liveDataHandler.dataPacketSignal.connect(self.updateFromDataPacket)
        
        self.widget = LimitWidget(num_channels, *args, **kwargs)
        self.setWindowTitle("Limits")
        self.setCentralWidget(self.widget)

        # save menu item
        self.save_action = QtGui.QAction("&Save Config", self.options_menu)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save)
        self.options_menu.addAction(self.save_action)

        # load menu item
        self.load_action = QtGui.QAction("&Load Config", self.options_menu)
        self.load_action.setShortcut("Ctrl+O")
        self.load_action.triggered.connect(self.load)
        self.options_menu.addAction(self.load_action)

        # set up environment and database
        self.interface = S2_Interface()
        self.channels = self.interface.channels
        self.header = ['time', 'packet_num', 'commander'] + self.channels
        self.database = pd.DataFrame(columns=self.header)
    
    def load(self):
        """Load config file"""
        self.widget.load()

    def save(self):
        """Saves config to a file"""
        self.widget.save()
    
    def exit(self):
        """Exit application"""
        #self.client_dialog.disconnect() #.client
        #app.quit()
        #sys.exit()

    def closeEvent(self, event):
        """Handler for closeEvent at window close"""

        self.exit()
    
    def cycle(self):
        self.widget.cycle()
    
    def update_limits(self, last_packet: dict):
        self.widget.update_limits(last_packet)

    @QtCore.pyqtSlot(object)
    def updateFromDataPacket(self, data_packet: dict):
        self.update_limits(data_packet)


if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()

    # initialize application
    appid = 'MASA.Limits'  # arbitrary string
    app.setApplicationName("MASA GUI")
    app.setApplicationDisplayName("MASA GUI (Singular) - Limits")

    if os.name == 'nt':  # Bypass command because it is not supported on Linux
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    else:
        pass
        # NOTE: On Ubuntu 18.04 this does not need to done to display logo in task bar

    #app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    lwgui = BaseGui(app)
    limit = LimitWindow(8, gui=lwgui, singular=True)
    lwgui.setMainWindow(limit)

    limit.show()
    sys.exit(app.exec())
