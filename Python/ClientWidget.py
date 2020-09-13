from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import sys
import socket
import pickle
import time
import uuid
import queue
from LedIndicatorWidget import *


class ClientWidget(QtWidgets.QWidget):
    def __init__(self, commandable=True, *args, **kwargs):
        super(ClientWidget, self).__init__(*args, **kwargs)
        self.clientid = uuid.uuid4().hex
        #self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.command_queue = queue.Queue()
        self.is_commander = False
        self.is_connected = False

        # connection box init
        self.connection_widget = QtWidgets.QGroupBox("Server Connection")
        self.connection_layout = QtWidgets.QGridLayout()
        self.connection_widget.setLayout(self.connection_layout)
        self.host = QtWidgets.QLineEdit()
        self.connection_layout.addWidget(self.host, 0, 0)
        self.port = QtWidgets.QLineEdit()
        self.connection_layout.addWidget(self.port, 0, 2)
        self.connection_layout.addWidget(QtGui.QLabel(":"), 0, 1)
        self.connect_button = QtGui.QPushButton("Connect")
        self.connection_layout.addWidget(self.connect_button, 0, 3)
        self.connect_button.clicked.connect(lambda: self.connect())
        self.disconnect_button = QtGui.QPushButton("Disconnect")
        self.connection_layout.addWidget(self.disconnect_button, 0, 4)
        self.disconnect_button.clicked.connect(lambda: self.disconnect())
        self.clientid_label = QtGui.QLabel("UUID: %s" % self.clientid)
        self.connection_layout.setColumnStretch(0, 2)
        self.connection_layout.setColumnStretch(1, 0)
        self.connection_layout.setColumnStretch(2, 1)
        self.connection_layout.setColumnStretch(3, 1.5)
        self.connection_layout.setColumnStretch(4, 1.5)
        
        # command box init
        self.command_widget = QtWidgets.QGroupBox("Commanding")
        self.command_layout = QtWidgets.QGridLayout()
        self.command_widget.setLayout(self.command_layout)
        self.command_layout.addWidget(self.clientid_label, 0, 0)
        self.control_button = QtGui.QPushButton("Take/Give Control")
        self.command_layout.addWidget(self.control_button, 0, 1)
        self.control_button.clicked.connect(lambda: self.command_toggle())
        self.led = LedIndicator(self)
        self.led.setDisabled(True)  # Make the led non-clickable
        self.command_layout.addWidget(self.led, 0, 2)
        self.command_layout.setColumnStretch(0, 2)
        self.command_layout.setColumnStretch(1, 1)
        self.command_layout.setColumnStretch(2, 0)

        # top level widget layout
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.connection_widget)
        if commandable:
            self.layout.addWidget(self.command_widget)

        # populate host fields with local address
        self.host.setText(socket.gethostbyname(socket.gethostname()))
        self.port.setText(str(6969))
    
    def command(self, command, args=()):
        # build and add command to queue
        command_dict = {
            "clientid" : self.clientid,
            "command" : command,
            "args" : args
        }

        msg = pickle.dumps(command_dict)
        self.command_queue.put(msg)

        if command is not 0:
            print(command_dict)

    def connect(self):
        # try to make a connection with server
        try:
            #self.s.detach()
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.host.text(), int(self.port.text())))
            self.is_connected = True
        except:
            self.is_connected = False

    def disconnect(self):
        # send disconnect message
        self.command(4)

    def command_toggle(self):
        # toggle to take/give up command
        if self.is_commander:
            self.command(2)
        else:
            self.command(1)

    def cycle(self):
        try:
            # send do nothing if no command queued
            if self.command_queue.empty():
                self.command(0)

            # send next command
            self.s.sendall(self.command_queue.get())

            # get data
            data = self.s.recv(4096*4)
            packet = pickle.loads(data)
            #print(packet)
            #print(packet["dataframe"])
            
            # update command status
            if packet["commander"] == self.clientid:
                self.is_commander = True
            else:
                self.is_commander = False
            self.led.setChecked(self.is_commander)
            
            return packet["dataframe"]
        
        except:
            return None

if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    controller = ClientWidget(commandable=True)
    
    timer = QtCore.QTimer()
    timer.timeout.connect(controller.cycle)
    timer.start(50) # 20hz
    
    controller.show()
    app.exec()

        