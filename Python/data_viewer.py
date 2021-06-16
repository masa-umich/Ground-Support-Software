import ctypes
import os
import sys
import json
from datetime import datetime

import pandas as pd
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from Switch import Switch
from ColorButton import ColorButton
from s2Interface import S2_Interface
from ClientWidget import ClientDialog
from plotWidgetWrapper import PlotWidgetWrapper


class DataViewerDialog(QtWidgets.QDialog):
    def __init__(self, gui):
        super().__init__()
        pg.setConfigOption('background', (67, 67, 67))
        pg.setConfigOptions(antialias=True)

        print("pyqtgraph Version: " + pg.__version__)

        self.gui = gui
        self.data_viewer = DataViewerWindow(gui, num_channels=8, rows=1, cols=1, cycle_time=250)
        self.setWindowTitle("Data Viewer")
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.data_viewer)
        self.setLayout(self.layout)


class DataViewer(QtWidgets.QTabWidget):
    """
    Custom QtWidget to plot data
    """

    def __init__(self, gui, channels: list, cycle_time: int, num_channels: int = 4, *args, **kwargs):
        """Initializes DataViewer object.

        Args:
            channels (list): List of tememetry channels as strings
            cycle_time (int): Cycle time of application in ms
            num_channels (int, optional): Number of data channels in plot. Defaults to 4.
        """
        super().__init__(*args, **kwargs)

        # load data channels
        self.gui = gui
        self.channels = channels  # list of channel names
        self.num_channels = int(num_channels/2)  # number of unique data channels in plot
        self.cycle_time = cycle_time  # cycle time of application in ms
        self.default_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                               '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']  # stolen from matplotlib

        # Some support if the gui is not attached
        if self.gui is None:
            self.font_scale_ratio = 1
        else:
            self.font_scale_ratio = self.gui.font_scale_ratio

        # initialize tabs
        self.config_tab = QtWidgets.QWidget()
        self.plot_tab = QtWidgets.QWidget()
        self.plot_layout = QtWidgets.QVBoxLayout()
        self.plot_layout.setContentsMargins(10, 10, 10, 10)
        self.plot_tab.setLayout(self.plot_layout)

        # Create plot
        self.plot2 = PlotWidgetWrapper()
        self.plot_layout.addWidget(self.plot2)

        # Add in tabs
        self.addTab(self.plot_tab, "Plot")
        self.addTab(self.config_tab, "Config")

        # Sets current tab to be config
        self.setCurrentIndex(1)

        # Set up config
        completer = QtWidgets.QCompleter(self.channels)  # channel autocomplete
        completer.setCaseSensitivity(False)


        # Globalize config. This is used for knowing what channels to duplicate when loading past data.
        self.config = None

        # Create grid layout to put everything in
        self.config_layout = QtWidgets.QGridLayout()
        self.config_tab.setLayout(self.config_layout)
        self.switches = []  # L/R switches
        self.series = []  # channel inputs
        self.aliases = []  # channel input alias
        self.colors = []  # color selector
        self.curves = []  # pyqtgraph curve objects

        # Spacing of the grid layout
        self.config_layout.setColumnStretch(0, 15)
        self.config_layout.setColumnStretch(1, 45)
        self.config_layout.setColumnStretch(2, 40)
        self.config_layout.setColumnStretch(3, 5)

        # Create input for title label
        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("Plot Title")
        self.config_layout.addWidget(self.title_edit, 0, 1, 1, 2)
        font = QtGui.QFont()
        font.setPointSize(12 * self.font_scale_ratio)
        self.title_edit.setFont(font)
        self.title_edit.editingFinished.connect(self.title_update)

        # Loop through the number of channels and populate the grid layout to contain all the inputs
        for i in range(num_channels):
            # Left/ right axis switch
            self.switches.append(Switch())
            self.switches[i].clicked.connect(
                lambda state: self.redraw_curves())
            self.config_layout.addWidget(self.switches[i], i + 1, 0)

            # Attach a curve
            self.curves.append(pg.PlotCurveItem())

            # Channel dropdown with autocomplete
            channel_dropdown = QtWidgets.QLineEdit()
            font = channel_dropdown.font()
            font.setPointSize(12 * self.font_scale_ratio)
            channel_dropdown.setFont(font)
            channel_dropdown.setCompleter(completer)
            channel_dropdown.setPlaceholderText("Channel Name")
            channel_dropdown.editingFinished.connect(lambda: self.redraw_curves())
            self.series.append(channel_dropdown)
            self.config_layout.addWidget(self.series[i], i + 1, 1)

            # Alias dropdown
            alias_dropdown = QtWidgets.QLineEdit()
            font = alias_dropdown.font()
            font.setPointSize(12 * self.font_scale_ratio)
            alias_dropdown.setFont(font)
            alias_dropdown.setPlaceholderText("Alias")
            alias_dropdown.editingFinished.connect(lambda: self.redraw_curves())
            self.aliases.append(alias_dropdown)
            # TODO: Connect this to something
            self.config_layout.addWidget(self.aliases[i], i + 1, 2)

            # Color picker
            self.colors.append(ColorButton(
                default_color=self.default_colors[i]))
            self.colors[i].colorChanged.connect(lambda: self.redraw_curves())
            self.config_layout.addWidget(self.colors[i], i + 1, 3)

        # setup duration field
        self.duration_edit = QtWidgets.QLineEdit("30")
        self.duration_label = QtWidgets.QLabel("Seconds")
        self.config_layout.addWidget(self.duration_edit, num_channels + 1, 0)
        self.config_layout.addWidget(self.duration_label, num_channels + 1, 1)
        self.duration_edit.editingFinished.connect(self.duration_update)
        self.duration_update()

        # setup 2 axis plot
        self.plot2.setBackgroundColor(40, 40, 40)
        self.plot2.setTitle(" ")

        self.plot2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.plot2.setAxisLabel("left", " ")
        self.plot2.setAxisLabelColor("bottom", "#FFF")  # who the fuck knows why this has to be hex
        self.plot2.setAxisLabelColor("right", "#FFF")
        self.plot2.setAxisLabelColor("left", "#FFF")

        self.plot2.setAxisTickFont("bottom", font)
        self.plot2.setAxisTickFont("left", font)
        self.plot2.setAxisTickFont("right", font)
        self.plot2.setTitle(" ")

        self.plot2.setLegendFontColor(255, 255, 255)
        self.plot2.setLegendTextSize(15)

        self.plot2.showLegend()

        self.plot2.setTitleSize("22pt")
        self.plot2.setTitleColor("w")

        self.plot2.showGrid(True, True, 0.3)

        self.plot2.setMouseEnabled(False, False)

        # self.plot2.addInfiniteLineCurve("Teset", QColor(255,255,0), 0.4, 0, "left")

        self.plot2.addCurve("Garbage", self.colors[0].color(), axis="left")
        self.plot2.addCurveLabelAlias("Garbage", "Aliased Name")
        self.plot2.curves["Garbage"].setData(x=np.array([0, 1, 5, 10, 12, 20, 24, 27, 30]),
                                             y=np.array([0, 15, 20, 21, 22, 21, 28, 26, 32]))
        self.plot2.addCurveLabelAlias("Garbage", "Aliased Name")

        self.plot2.showLegend()

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
            curve_config = config[i + 2]
            self.switches[i].setChecked(bool(curve_config[0]))

            self.colors[i].setColor(curve_config[2])
            if(curve_config[1] == ""):
                self.series[i].setText("buffer")
            else:
                self.series[i].setText(curve_config[1])

            self.plot2.addCurve(curve_config[1], curve_config[2], curve_config[0])
        self.redraw_curves()



        # Globalize config. This is used for knowing what channels to duplicate when loading past data.
        self.config = config
        #print(len(config))
        #(self.plot2.curves)

    def save_config(self):
        """Returns save config

        Returns:
            list: Save config
        """
        config = [self.title_edit.text(), self.duration_edit.text()]
        for i in range(2*self.num_channels):
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

        # Remove all curves to start
        self.plot2.removeAllCurves()

        # Loop through all channels
        hasRight = False
        for idx in range(2*self.num_channels):
            # Check if the switch is checked and if so place everything on right axis
            axis = "left"  # default
            if self.switches[idx].isChecked():
                axis = "right"
                hasRight = True
                if self.plot2.right_view_box is None:
                    self.plot2.addRightAxis()

            # Get the color of the line
            color = QColor(255, 255, 255)  # defualt
            if self.colors[idx].color():
                color = QColor(self.colors[idx].color())

            # Add curves back in
            # TODO: Add in alias junk here
            parsed = self.series[idx].text().split("=")  # Parse for line=xx to see if that was inputted
            if len(parsed[0]) > 0:
                # If the parse finds nothing then parsed[0] will be the uncut string
                if parsed[0] == "line" and len(parsed) == 2:
                    self.curves[idx] = self.plot2.addInfiniteLineCurve(self.series[idx].text(), color, parsed[1], 0,
                                                                       axis=axis)

                else:
                    self.curves[idx] = self.plot2.addCurve(parsed[0], color, axis=axis)
                    if self.aliases[idx].text() is not "":
                        self.plot2.addCurveLabelAlias(parsed[0], self.aliases[idx].text())

        if not hasRight and self.plot2.right_view_box is not None:
            self.plot2.hideRightAxis()

        self.plot2.showLegend()

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
        self.plot2.setTitle(self.title_edit.text())

    def duration_update(self):
        """Updates plot duration on field edit"""
        self.duration = int(self.duration_edit.text())
        self.plot2.setAxisLabel("bottom", "Time: -" + self.duration_edit.text() + " seconds")
        self.plot2.setXRange(0, self.duration)

    def update(self, frame: pd.DataFrame):
        """Updates plot with new data

        Args:
            frame (pandas.DataFrame): Pandas DataFrame of telemetry data
        """
        # super().update()
        points = int(self.duration * 1000 / self.cycle_time)
        data = frame.tail(points)
        for i in range(2*self.num_channels):
            # get channel name
            channel_name = self.series[i].text()
            if channel_name in self.channels:
                self.plot2.curves[channel_name].setData(
                    x=data["time"].to_numpy(), y=data[channel_name].to_numpy())

    def update_load(self, frame: pd.DataFrame, window_num_load: int):
        """Updates plot with new data. The reason we need this is that the channels have been duplicated.

        Args:
            frame (pandas.DataFrame): Pandas DataFrame of telemetry data
            window_num_load (int): passed from dataViewerWindow, used along the naming of frame
        """
        #print(self.config)
        #print("pass")
        #replicate current config for new set of data
        for i in range(self.num_channels):
            channel_pos = self.num_channels + i
            curve_config = self.config[i+ 2] #this is still i cus its the original
            #print(self.config[i+2])
            # Rename the channels
            root_name = curve_config[1]
            curve_config[1] = root_name + "_LOADED_" + str(window_num_load)
            # instantiate more channels
            # Attach a curve
            self.curves.append(pg.PlotCurveItem())
            # fill in infor about channels
            self.switches[channel_pos].setChecked(bool(curve_config[0]))
            self.series[channel_pos].setText(curve_config[1])
            self.colors[channel_pos].setColor(curve_config[2])
            self.plot2.addCurve(curve_config[1], curve_config[2], curve_config[0])
            self.plot2.showLegend()

        self.redraw_curves()


        # Load in the data points
        points = int(self.duration * 1000 / self.cycle_time)
        data = frame.tail(points)
        suffix = "_LOADED_" + str(window_num_load)
        print(self.channels)
        print(suffix)
        for i in range(self.num_channels):
            #print(i)
            channel_pos = self.num_channels + i
            # get channel name
            channel_name = self.series[channel_pos].text()
            print(channel_name)
            buffer_name = self.series[channel_pos].text()
            print((channel_name in self.channels and suffix in channel_name))
            if (channel_name in self.channels and suffix in channel_name and channel_name in data):
                #print(self.plot2.curves)
                # self.channels comes from the csv and I appended the _LOADED_ ones. channel_name comes from self.series
                self.plot2.curves[channel_name].setData(
                    x=data["time" + "_LOADED_" + str(window_num_load)].to_numpy(),
                    y=data[channel_name].to_numpy())


class DataViewerWindow(QtWidgets.QMainWindow):
    """
    Window with client and DataViewer objects
    """

    def __init__(self, gui=None, num_channels: int = 4, rows: int = 3, cols: int = 3, cycle_time: int = 250,
                 client=None, *args, **kwargs):
        """Initializes window

        Args:
            num_channels (int, optional): Number of channels in each viewer. Defaults to 4.
            rows (int, optional): Rows of viewers. Defaults to 3.
            cols (int, optional): Columns of viewers. Defaults to 3.
            cycle_time (int, optional): Refresh time of each loop in ms. Used for calculating lot durations. Defaults to 250 ms.
        """
        super().__init__(*args, **kwargs)
        # window top-level layout
        self.gui = gui
        self.setWindowTitle("MASA Data Viewer")
        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)
        self.top_layout = QtWidgets.QGridLayout()
        self.widget.setLayout(self.top_layout)

        self.rows = rows
        self.cols = cols
        self.num_channels = num_channels
        self.cycle_time = cycle_time

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

        # Add row of graphs to view
        self.row_action = QtGui.QAction("&Add Row", self.options_menu)
        self.row_action.setShortcut("Ctrl+R")
        self.row_action.triggered.connect(self.addRow)
        self.options_menu.addAction(self.row_action)

        # Add col of graphs to view
        self.col_action = QtGui.QAction("&Add Column", self.options_menu)
        self.col_action.setShortcut("Ctrl+C")
        self.col_action.triggered.connect(self.addCol)
        self.options_menu.addAction(self.col_action)

        # Load data
        self.load_data_action = QtGui.QAction("&Load data", self.options_menu)
        self.load_data_action.triggered.connect(self.loadData)
        self.options_menu.addAction(self.load_data_action)
        self.num_load = 0;

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
            self.gui, self.channels, cycle_time, num_channels=num_channels) for i in range(rows * cols)]
        for i in range(rows):
            for j in range(cols):
                idx = i * cols + j
                self.top_layout.addWidget(self.viewers[idx], i, j)

        self.starttime = datetime.now().timestamp()
        self.cycle_time = cycle_time

    def addRow(self):

        for i in range(self.cols):
            self.viewers.append(
                DataViewer(self.gui, self.channels, cycle_time=self.cycle_time, num_channels=self.num_channels))
            self.top_layout.addWidget(self.viewers[-1], self.rows, i)

        self.rows = self.rows + 1

    def addCol(self):

        for i in range(self.rows):
            self.viewers.append(
                DataViewer(self.gui, self.channels, cycle_time=self.cycle_time, num_channels=self.num_channels))
            self.top_layout.addWidget(self.viewers[-1], i, self.cols)

        self.cols = self.cols + 1

    # loop
    def update(self):
        """Update application"""
        # super().update()
        self.last_packet = self.client_dialog.client.cycle()

        if self.client_dialog.client.is_connected:
            self.last_packet["time"] -= self.starttime  # time to elapsed
            last_frame = pd.DataFrame(self.last_packet, index=[0])
            self.database = pd.concat([self.database, last_frame], axis=0, ignore_index=True).tail(
                int(15 * 60 * 1000 / self.cycle_time))  # cap data to 15 min

        # maybe only run if connection established?
        for viewer in self.viewers:
            if viewer.is_active():
                viewer.update(self.database)

    def loadData(self):
        """Load data from a log file (csv).
        This function can be called multiple times (?) to load data before graphing live data, or to load 2 log files."""

        # keep track of how many files have been loaded
        self.num_load += 1

        # select a csv file
        loadname = QtGui.QFileDialog.getOpenFileName(
            self, "Load Data", "", "Data log (*.csv)")[0]

        # read in csv as DataFrame
        with open(loadname, "r") as file:
            df = pd.read_csv(file)

        self.renameDF(df)

        # If multiple files are loaded (or if we are also graphing live data), add suffix to config
        for viewer in self.viewers:
            for i in range(viewer.num_channels):
                viewer.channels.append(viewer.config[i+2][1] + "_LOADED_" + str(self.num_load))
                # TODO: maybe fade the hex color, viewer.config[i+2][2]

        # delete the first empty line in the csv
        df.drop(df.index[0])

        for viewer in self.viewers:
            if viewer.is_active():
                viewer.update_load(df, self.num_load)



    def renameDF(self, df: pd.DataFrame):
        """
        The log files have units attached to the headers of the DataFrame so they can not be recognized by channels.
        This function removed the units and added the suffix to match the channel names.
        """
        dictWithoutUnits = {
            column: column.split()[0] + "_LOADED_" + str(self.num_load)
            for column in df.columns
        }
        df.rename(columns=dictWithoutUnits, inplace=True)
        df.rename(columns={'Time': 'time'})


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

    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()

    # This has to be done early on, dark mode rn
    pg.setConfigOption('background', (67, 67, 67))
    pg.setConfigOptions(antialias=True)

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
    window = DataViewerWindow(num_channels=8, rows=1,
                              cols=1, cycle_time=CYCLE_TIME)

    # timer and tick updates
    timer = QtCore.QTimer()
    timer.timeout.connect(window.update)
    timer.start(CYCLE_TIME)

    # TODO: Add in light mode
    print("Python Version:" + str(sys.version_info))
    print("QT Version: " + QT_VERSION_STR)

    app.setStyle("Fusion")

    darkPalette = QPalette()
    darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.WindowText, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Base, QColor(42, 42, 42))
    darkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    darkPalette.setColor(QPalette.ToolTipBase, Qt.black)
    darkPalette.setColor(QPalette.ToolTipText, Qt.white)
    darkPalette.setColor(QPalette.Text, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Dark, QColor(35, 35, 35))
    darkPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
    darkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ButtonText, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.BrightText, Qt.red)
    darkPalette.setColor(QPalette.Link, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    darkPalette.setColor(QPalette.HighlightedText, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))

    app.setPalette(darkPalette)

    # run
    window.show()
    sys.exit(app.exec())
