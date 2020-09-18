from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import ctypes
import os
import pandas as pd
from DataViewer import DataViewer
from hotfire_packet import ECParse
from ClientWidget import ClientWidget, ClientDialog
import sys
import json


class DataViewerWindow(QtWidgets.QMainWindow):
    def __init__(self, num_channels=4, rows=3, cols=3, cycle_time=250, *args, **kwargs):
        super(DataViewerWindow, self).__init__(*args, **kwargs)
        # layout
        self.setWindowTitle("MASA Data Viewer")
        self.w = QtWidgets.QWidget()
        self.setCentralWidget(self.w)
        self.top_layout = QtWidgets.QGridLayout()
        self.w.setLayout(self.top_layout)

        # set up client
        self.client_dialog = ClientDialog(False)

        #menu bar
        self.main_menu = self.menuBar()
        self.main_menu.setNativeMenuBar(True)
        self.options_menu = self.main_menu.addMenu('&Options')

        # connection menu item
        self.quit = QtGui.QAction("&Connection", self.options_menu)
        #self.quit.setShortcut("Ctrl+K")
        self.quit.triggered.connect(self.exit)
        self.options_menu.addAction(self.quit)

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

        #quit application menu item
        self.quit = QtGui.QAction("&Quit", self.options_menu)
        self.quit.setShortcut("Ctrl+Q")
        self.quit.triggered.connect(self.exit)
        self.options_menu.addAction(self.quit)

        # set up environment and database
        self.parser = ECParse()
        self.channels = [item for item in self.parser.items if (item is not 'zero' and item is not '')]
        self.header = ['time', 'packet_num', 'commander'] + self.channels
        self.database = pd.DataFrame(columns=self.header)
        
        # init viewers
        self.viewers = [DataViewer(self.channels, cycle_time, num_channels=num_channels) for i in range(rows*cols)]
        for i in range(rows):
            for j in range(cols):
                idx = i*3+j
                self.top_layout.addWidget(self.viewers[idx], i, j)
        
    # loop
    def update(self):
        self.last_packet = self.client_dialog.client.cycle()
        if self.client_dialog.client.is_connected:
            last_frame = pd.DataFrame.from_dict(self.last_packet)
            self.database = pd.concat([self.database, last_frame], axis=0, ignore_index=True)
        per_viewer_actives = [viewer.getActive() for viewer in self.viewers]
        self.active_channels = list(set([channel for viewer in per_viewer_actives for channel in viewer])) # kill me now
        #print(self.active_channels)
        # maybe only run if connection established?
        for viewer in self.viewers:
            if viewer.isActive():
                viewer.update(self.database)
    
    # quit application function
    def exit(self):
        self.client_dialog.client.disconnect()
        app.quit()
        sys.exit()

    # show connection dialog
    def showConnection(self):
        self.client_dialog.show()
    
    # viewer config load/save (TODO)
    def load(self):
        loadname = QtGui.QFileDialog.getOpenFileName(self, "Load Config", "", "Config (*.cfg)")[0]
        with open(loadname, "r") as f:
            config = json.load(f)
        for i in range(len(self.viewers)):
            self.viewers[i].loadConfig(config[i])
    
    # save config
    def save(self):
        configs = [viewer.saveConfig() for viewer in self.viewers]
        savename = QtGui.QFileDialog.getSaveFileName(self, 'Save Config', 'dataviewer.cfg', "Config (*.cfg)")[0]
        with open(savename, "w") as f:
            json.dump(configs, f)


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
    app.setWindowIcon(QtGui.QIcon('logo_server.png'))

    # init window
    cycle_time = 1000 # in ms
    window = DataViewerWindow(num_channels=4, rows=3, cols=3, cycle_time=cycle_time)

    #timer and tick updates
    timer = QtCore.QTimer()
    timer.timeout.connect(window.update)
    timer.start(cycle_time)

    # run
    window.show()
    sys.exit(app.exec())