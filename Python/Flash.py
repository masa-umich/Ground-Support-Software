from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import sys
import os

from constants import Constants
from s2Interface import S2_Interface

#import socket
#import json
#import pickle
#import time
#import uuid
#import queue
#from LedIndicatorWidget import LedIndicator

class FlashDialog(QtWidgets.QDialog):
    def __init__(self, client):
        super().__init__()
        self.flash_controller = FlashController(client)

        self.setWindowTitle("Flash Controller")
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.flash_controller)
        self.setLayout(self.layout)

class FlashController(QtWidgets.QWidget):
    def __init__(self, client, *args, **kwargs):
        super(FlashController, self).__init__(*args, **kwargs)
        self.interface = S2_Interface()
        self.client = client

        # logo
        self.logo = QtGui.QLabel()
        pixmap_scaled = QtGui.QPixmap("flash.png").scaled(400, 400, QtCore.Qt.KeepAspectRatio)
        self.logo.setPixmap(pixmap_scaled)
        self.logo.setAlignment(QtCore.Qt.AlignCenter)

        self.board_selector = QtWidgets.QComboBox()
        self.file_selector = QtWidgets.QLineEdit()
        self.file_button = QtWidgets.QPushButton("Select")
        self.download_button = QtWidgets.QPushButton("Download")
        self.wipe_button = QtWidgets.QPushButton("Wipe Flash")
        self.start_button = QtWidgets.QPushButton("Start Logging")
        self.stop_button = QtWidgets.QPushButton("Stop Logging")

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.logo, 0, 0, 1, 2)
        self.layout.addWidget(self.board_selector, 1, 0, 1, 2)
        self.layout.addWidget(self.file_selector, 2, 0, 1, 1)
        self.layout.addWidget(self.file_button, 2, 1, 1, 1)
        self.layout.addWidget(self.download_button, 3, 0, 1, 2) 
        self.layout.addWidget(self.wipe_button, 4, 0, 1, 2) 
        self.layout.addWidget(self.start_button, 5, 0, 1, 2) 
        self.layout.addWidget(self.stop_button, 6, 0, 1, 2) 

        self.board_selector.addItems(Constants.boards)

        self.file_button.clicked.connect(self.select_file)

    def select_file(self):
        options = QtWidgets.QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self,"Select Dump File","","Text Files (*.csv);;All Files (*)", options=options)
        if filename:
            self.file_selector.setText(filename)

    def dump(self):
        return
    
    def wipe(self):
        return
    
    def stop_logging(self):
        return

    def start_logging(self):
        return


    

if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    controller = FlashDialog(None)
    
    #timer = QtCore.QTimer()
    #timer.timeout.connect(controller.cycle)
    #timer.start(50) # in ms, 20hz
    
    controller.show()
    sys.exit(app.exec())

        