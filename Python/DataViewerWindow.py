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


class DataViewerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
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
        self.quit.triggered.connect(self.showConnection)
        self.options_menu.addAction(self.quit)

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
        rows = 3
        cols = 3
        self.viewers = [DataViewer(self.channels) for i in range(rows*cols)]
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
        for viewer in self.viewers:
            if viewer.isActive():
                viewer.update(self.database)
    
    #quit application function
    def exit(self):
        pass

    def showConnection(self):
        self.client_dialog.show()


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

    window = DataViewerWindow()

    #timer and tick updates
    timer = QtCore.QTimer()
    timer.timeout.connect(window.update)
    timer.start(250)

    # run
    window.show()
    sys.exit(app.exec())