import sys
import socket
import pickle
import uuid
import queue
import hashlib
import traceback

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow
import pyqtgraph as pg

from LedIndicatorWidget import LedIndicator


class ClientDialog(QtWidgets.QDialog):
    def __init__(self, client):
        super().__init__()

        self.client = client
        self.setWindowTitle("Connection")
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.client)
        self.setLayout(self.layout)


class ClientWidget(QtWidgets.QWidget):
    def __init__(self, commandable: bool=True, gui = None, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.clientid = uuid.uuid4().hex
        #self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.command_queue = queue.Queue()
        self.is_commander = False
        self.is_connected = False
        self.last_packet = None

        self._dialog = ClientDialog(self)

        self._gui = gui
        self.gui_window = self._gui.controlsWindow

        # connection box init
        self.connection_widget = QtWidgets.QGroupBox("Server Connection")
        self.connection_layout = QtWidgets.QGridLayout()
        self.connection_widget.setLayout(self.connection_layout)
        self.host = QtWidgets.QComboBox()
        self.host.addItems([socket.gethostbyname(
            socket.gethostname()), '192.168.50.79', 'masadataserver'])
        self.host.setEditable(True)
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
        self.connection_layout.setColumnStretch(0, 4)
        self.connection_layout.setColumnStretch(1, 0)
        self.connection_layout.setColumnStretch(2, 2)
        self.connection_layout.setColumnStretch(3, 3)
        self.connection_layout.setColumnStretch(4, 3)

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
        # self.host.setText(socket.gethostbyname(socket.gethostname()))
        self.port.setText(str(6969))

    def command(self, command: int, args: tuple=()):
        # build and add command to queue
        command_dict = {
            "clientid": self.clientid,
            "command": command,
            "args": args
        }

        msg = pickle.dumps(command_dict)
        # print(msg)

        if command != 0:
            print(command_dict)
            if self.gui_window is not None:
                if command_dict["command"] == 3:
                    self.gui_window.statusBar().showMessage("Command sent to server: " + str(command_dict["args"]))
                else:
                    self.gui_window.statusBar().showMessage("Command sent to client: " + str(command_dict))

        # add to queue
        if self.is_connected:
            self.command_queue.put(msg)

    def connect(self):
        # try to make a connection with server
        try:
            # setup socket interface
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.host.currentText(), int(
                self.port.text())))  # connect to socket

            self.is_connected = True  # update status
            if self.gui_window is not None:
                if not self.gui_window.gui.campaign.is_active:
                    self.gui_window.startRunAct.setEnabled(True)
                else:
                    self.command(6, [str(self.gui_window.gui.campaign.saveName)])
                self.gui_window.statusBar().showMessage(
                        "Connected to server on " + self.host.currentText() + ":" + self.port.text())

        except Exception as e:
            print(traceback.format_exc())
            self.is_connected = False  # update status
            self.gui_window.startRunAct.setDisabled(True)
        #print(self.is_connected)

    def disconnect(self):
        # send disconnect message
        self.command(4)
        self.is_connected = False
        if self.gui_window is not None:
            self.gui_window.statusBar().showMessage("Disconnected from server")
            self.gui_window.startRunAct.setDisabled(True)

    def command_toggle(self):
        # toggle to take/give up command
        if self.is_commander:
            self.command(2)
        else:
            self.command(1)

    def getDialog(self):
        return self._dialog

    def cycle(self):
        try:
            # send do nothing if no command queued
            if self.command_queue.empty():
                self.command(0)

            if self.is_connected:
                # send next command
                data = self.command_queue.get()
                self.s.sendall(data)

                # get data
                data = self.s.recv(4096*4)
                packet = pickle.loads(data)

            # update command status
            if packet["commander"] == None:
                self.is_commander = False
            elif packet["commander"] == hashlib.sha256(self.clientid.encode('utf-8')).hexdigest():
                self.is_commander = True
            else:
                self.is_commander = False
            self.led.setChecked(self.is_commander)

            self.last_packet = packet
            return self.last_packet

        except:
            #traceback.print_exc()
            self.is_connected = False
            return None


if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    controller = ClientWidget(commandable=True)

    timer = QtCore.QTimer()
    timer.timeout.connect(controller.cycle)
    timer.start(50)  # in ms, 20hz

    controller.show()
    sys.exit(app.exec())
