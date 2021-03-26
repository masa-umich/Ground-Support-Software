import ctypes
import os
import sys
import json
from datetime import datetime

import pandas as pd
import pyqtgraph as pg
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt

from Switch import Switch
from ColorButton import ColorButton
from s2Interface import S2_Interface
from ClientWidget import ClientDialog


class DataViewer(QtWidgets.QTabWidget):
    """
    Custom QtWidget to plot data
    """

    def __init__(self, channels: list, cycle_time: int, num_channels: int = 4, *args, **kwargs):
        """Initializes DataViewer object.

        Args:
            channels (list): List of tememetry channels as strings
            cycle_time (int): Cycle time of application in ms
            num_channels (int, optional): Number of data channels in plot. Defaults to 4.
        """
        super().__init__(*args, **kwargs)

        # load data channels
        self.channels = channels  # list of channel names
        self.num_channels = num_channels  # number of data channels in plot
        self.cycle_time = cycle_time  # cycle time of application in ms
        self.default_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                               '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']  # stolen from matplotlib

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
        completer = QtWidgets.QCompleter(self.channels)  # channel autocomplete
        completer.setCaseSensitivity(False)
        self.config_layout = QtWidgets.QGridLayout()
        self.config_tab.setLayout(self.config_layout)
        self.switches = []  # L/R switches
        self.series = []  # channel inputs
        self.colors = []  # color selector
        self.curves = []  # pyqtgraph curve objects

        # plot title
        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("Plot Title")
        self.config_layout.addWidget(self.title_edit, 0, 1)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.title_edit.setFont(font)
        self.title_edit.editingFinished.connect(self.title_update)

        # setup channel rows
        for i in range(num_channels):
            self.switches.append(Switch())
            self.switches[i].clicked.connect(
                lambda state: self.redraw_curves())
            self.curves.append(pg.PlotCurveItem())
            self.config_layout.addWidget(self.switches[i], i+1, 0)
            dropdown = QtWidgets.QLineEdit()
            font = dropdown.font()
            font.setPointSize(12)
            dropdown.setFont(font)
            dropdown.setCompleter(completer)
            dropdown.editingFinished.connect(lambda: self.redraw_curves())
            self.series.append(dropdown)
            self.config_layout.addWidget(self.series[i], i+1, 1)
            self.colors.append(ColorButton(
                default_color=self.default_colors[i]))
            self.colors[i].colorChanged.connect(lambda: self.redraw_curves())
            self.config_layout.addWidget(self.colors[i], i+1, 2)

        # setup duration field
        self.duration_edit = QtWidgets.QLineEdit("30")
        self.duration_label = QtWidgets.QLabel("Seconds")
        self.config_layout.addWidget(self.duration_edit, num_channels+1, 0)
        self.config_layout.addWidget(self.duration_label, num_channels+1, 1)
        self.duration_edit.editingFinished.connect(self.duration_update)
        self.duration_update()

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
        self.view_update()
        self.left.vb.sigResized.connect(self.view_update)

        # Plot formatting
        font = QtGui.QFont()
        font.setPixelSize(14)
        self.left.getAxis("bottom").setTickFont(font)
        self.left.getAxis("left").setTickFont(font)
        self.left.getAxis("right").setTickFont(font)
        self.left.showGrid(True, True)
        self.left.legend.setOffset((5, 5))
        self.plot.setMouseEnabled(False, False)

    def load_config(self, config: list):
        """Loads a DataViewer config

        Args:
            config (list): DataViewer config
        """
        self.title_edit.setText(config[0])
        self.title_update()
        self.duration_edit.setText(config[1])
        self.duration_update()
        for i in range(self.num_channels):
            curve_config = config[i+2]
            self.switches[i].setChecked(bool(curve_config[0]))
            self.series[i].setText(curve_config[1])
            self.colors[i].setColor(curve_config[2])
        self.redraw_curves()

    def save_config(self):
        """Returns save config

        Returns:
            list: Save config
        """
        config = [self.title_edit.text(), self.duration_edit.text()]
        for i in range(self.num_channels):
            config.append([self.switches[i].isChecked(),
                           self.series[i].text(), self.colors[i].color()])
        return config

    def print_curves(self):
        """Debug function to dump children of plots to console"""
        print("right: " +
              str([dataobj for dataobj in self.right.allChildren()]))
        print(
            "left: " + str([dataobj for dataobj in self.left.getViewBox().allChildren()]))

    def redraw_curves(self):
        """Redraws plot anytime paramaters are changed"""
        # remove curves from legend
        self.left.legend.clear()

        if self.is_active():
            # draw when plots active
            self.left.legend.setBrush(pg.mkBrush(
                255, 255, 255, 255))  # background
            self.left.legend.setPen(pg.mkPen(0, 0, 0, 100))  # border
        else:
            # hide when not active
            self.left.legend.setBrush(None)
            self.left.legend.setPen(None)

        for idx in range(self.num_channels):
            # remove curve from plot
            for dataobj in self.right.allChildren():
                if dataobj is self.curves[idx]:
                    self.right.removeItem(dataobj)

            for dataobj in self.left.getViewBox().allChildren():
                if dataobj is self.curves[idx]:
                    self.left.removeItem(dataobj)

            # handle lines
            parsed = self.series[idx].text().split("=")  # parse
            if len(parsed[0]) > 0:
                if (parsed[0] == "line" and len(parsed) == 2):
                    self.curves[idx] = pg.InfiniteLine(
                        pos=parsed[1], angle=0)  # add infinite line
                else:
                    self.curves[idx] = pg.PlotCurveItem()  # add standard curve
                    self.left.legend.addItem(
                        self.curves[idx], parsed[0])  # add to legend

            # set curve color
            if self.colors[idx].color():
                self.curves[idx].setPen(
                    pg.mkPen(QtGui.QColor(self.colors[idx].color())))

            # set curve to left or right side
            if self.switches[idx].isChecked():
                self.right.addItem(self.curves[idx])
            else:
                self.left.addItem(self.curves[idx])

    def view_update(self):
        """Resize plot on window resize"""
        self.right.setGeometry(self.left.vb.sceneBoundingRect())
        self.right.linkedViewChanged(self.left.vb, self.right.XAxis)

    def get_active(self):
        """Returns a list of all the active channels

        Returns:
            list: Active channels
        """
        return [str(s.text()) for s in self.series if str(s.text()) != ""]

    def is_active(self):
        """Returns True if plot is configured with a channel

        Returns:
            bool: Is the plot active?
        """
        return len(self.get_active()) > 0

    def title_update(self):
        """Updates plot title"""
        self.plot.setTitle(self.title_edit.text())

    def duration_update(self):
        """Updates plot duration on field edit"""
        self.duration = int(self.duration_edit.text())

    def update(self, frame: pd.DataFrame):
        """Updates plot with new data

        Args:
            frame (pandas.DataFrame): Pandas DataFrame of telemetry data
        """
        # super().update()
        points = int(self.duration*1000/self.cycle_time)
        data = frame.tail(points)
        for i in range(self.num_channels):
            # get channel name
            channel_name = self.series[i].text()
            if channel_name in self.channels:
                self.curves[i].setData(
                    x=data["time"].to_numpy(), y=data[channel_name].to_numpy())


class DataViewerWindow(QtWidgets.QMainWindow):
    """
    Window with client and DataViewer objects
    """

    def __init__(self, num_channels: int = 4, rows: int = 3, cols: int = 3, cycle_time: int = 250, client=None, *args, **kwargs):
        """Initializes window

        Args:
            num_channels (int, optional): Number of channels in each viewer. Defaults to 4.
            rows (int, optional): Rows of viewers. Defaults to 3.
            cols (int, optional): Columns of viewers. Defaults to 3.
            cycle_time (int, optional): Refresh time of each loop in ms. Used for calculating lot durations. Defaults to 250 ms.
        """
        super().__init__(*args, **kwargs)
        # window top-level layout
        self.setWindowTitle("MASA Data Viewer")
        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)
        self.top_layout = QtWidgets.QGridLayout()
        self.widget.setLayout(self.top_layout)

        # set up client
        if not client:
            self.client_dialog = ClientDialog(False)
        else:
            self.client_dialog = client

        self.last_packet = None

        # menu bar
        self.main_menu = self.menuBar()
        self.main_menu.setNativeMenuBar(True)
        self.options_menu = self.main_menu.addMenu('&Options')

        # connection menu item
        if not client:
            self.connect = QtGui.QAction("&Connection", self.options_menu)
            # self.quit.setShortcut("Ctrl+K")
            self.connect.triggered.connect(self.client_dialog.show)
            self.options_menu.addAction(self.connect)

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

        # quit application menu item
        self.quit = QtGui.QAction("&Quit", self.options_menu)
        self.quit.setShortcut("Ctrl+Q")
        self.quit.triggered.connect(self.exit)
        self.options_menu.addAction(self.quit)

        # set up environment and database
        self.interface = S2_Interface()
        self.channels = self.interface.channels
        self.header = ['time', 'packet_num', 'commander'] + self.channels
        self.database = pd.DataFrame(columns=self.header)

        # init viewers
        self.viewers = [DataViewer(
            self.channels, cycle_time, num_channels=num_channels) for i in range(rows*cols)]
        for i in range(rows):
            for j in range(cols):
                idx = i*cols+j
                self.top_layout.addWidget(self.viewers[idx], i, j)

        self.starttime = datetime.now().timestamp()
        self.cycle_time = cycle_time

    # loop
    def update(self):
        """Update application"""
        # super().update()
        self.last_packet = self.client_dialog.client.cycle()

        if self.client_dialog.client.is_connected:
            self.last_packet["time"] -= self.starttime  # time to elapsed
            last_frame = pd.DataFrame(self.last_packet, index=[0])
            self.database = pd.concat([self.database, last_frame], axis=0, ignore_index=True).tail(
                int(15*60*1000/self.cycle_time))  # cap data to 15 min

        # maybe only run if connection established?
        for viewer in self.viewers:
            if viewer.is_active():
                viewer.update(self.database)

    def exit(self):
        """Exit application"""
        self.client_dialog.client.disconnect()
        app.quit()
        sys.exit()

    def show_connection(self):
        """Show connection dialog"""
        self.client_dialog.show()

    def load(self):
        """Load config file"""
        loadname = QtGui.QFileDialog.getOpenFileName(
            self, "Load Config", "", "Config (*.cfg)")[0]
        with open(loadname, "r") as file:
            configs = json.load(file)
        for i in range(len(self.viewers)):
            self.viewers[i].load_config(configs[i])

    def save(self):
        """Saves config to a file"""
        configs = [viewer.save_config() for viewer in self.viewers]
        savename = QtGui.QFileDialog.getSaveFileName(
            self, 'Save Config', 'dataviewer.cfg', "Config (*.cfg)")[0]
        with open(savename, "w") as file:
            json.dump(configs, file)


if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QtWidgets.QApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    #QtWidgets.QApplication.setHigh

    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()

    # initialize application
    APPID = 'MASA.DataViewer'  # arbitrary string
    if os.name == 'nt':  # Bypass command because it is not supported on Linux
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
    else:
        pass
        # NOTE: On Ubuntu 18.04 this does not need to done to display logo in task bar
    app.setWindowIcon(QtGui.QIcon('Images/logo_server.png'))

    # init window
    CYCLE_TIME = 250  # in ms
    window = DataViewerWindow(num_channels=4, rows=2,
                              cols=2, cycle_time=CYCLE_TIME)

    # timer and tick updates
    timer = QtCore.QTimer()
    timer.timeout.connect(window.update)
    timer.start(CYCLE_TIME)

    # run
    window.show()
    sys.exit(app.exec())

