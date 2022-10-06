import sys
import socket
import pickle
import uuid
import queue
import hashlib
import traceback

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow
import pyqtgraph as pg

from LedIndicatorWidget import LedIndicator


class ClientDialog(QtWidgets.QDialog):
    def __init__(self, client, gui):
        super().__init__()

        if client is not None:
            self.client = client
        else:
            self.client = ClientWidget(commandable=False, gui=gui) # this needs a gui
        self.setWindowTitle("Connection")
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.client)
        self.setLayout(self.layout)


class ClientWidget(QtWidgets.QWidget):

    gotConnectionToServerSignal = pyqtSignal()
    serverDisconnectSignal = pyqtSignal()

    def __init__(self, commandable: bool=True, gui = None, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.clientid = uuid.uuid4().hex
        #self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.command_queue = queue.Queue()
        self.is_commander = False
        self.is_connected = False
        self.last_packet = None

        self._dialog = ClientDialog(self, gui)

        if gui is not None:
            self._gui = gui

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
            if command_dict["command"] == 3:
                self._gui.setStatusBarMessage("Command sent to server: " + str(command_dict["args"]))
            else:
                # TODO: What??
                self._gui.setStatusBarMessage("Command sent to client: " + str(command_dict))

        # add to queue
        if self.is_connected:
            self.command_queue.put(msg)

    def connect(self):
        # try to make a connection with server
        try:
            # setup socket interface
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.settimeout(1)
            self.s.connect((self.host.currentText(), int(
                self.port.text())))  # connect to socket
            self.s.settimeout(None)  #  from https://stackoverflow.com/questions/3432102/python-socket-connection-timeout to prevent blocking
            self.is_connected = True  # update status
            self.command(11)
            self.gotConnectionToServerSignal.emit()
            print("Connected to server on " + self.host.currentText() + ":" + self.port.text())
            self._gui.setStatusBarMessage("Connected to server on " + self.host.currentText() + ":" + self.port.text())

        except Exception as e:
            print(traceback.format_exc())
            self._gui.setStatusBarMessage("Error connecting to server, see terminal", True)
            self.soft_disconnect()
        #print(self.is_connected)

    def disconnect(self):
        """
        This function is called when the user disconnects from server. For cases where the server side is terminated,
        the server errors out the connection, server crashes, etc then this is not called but instead soft disconnect is
        called. Reason being that in those cases we cannot send a command to disconnect, yet still need to perform
        some client side actions for cleanup
        :return: None
        """
        # Make sure we are actually connected before we try to disconnect
        if self.is_connected:
            self.command(4)
            self.cycle()  # need to get the last command out before saying we are disconnected
            self.soft_disconnect()

    def soft_disconnect(self):
        """
        Performs all the required steps when client and server are disconnected, however it does not send any commands
        to the server that indicate the client is attempting to disconnect. See above disconnect for more
        :return:
        """
        self.s.close()
        self.is_connected = False
        self.serverDisconnectSignal.emit()  # See gui class for what needs to be done
        self._gui.setStatusBarMessage("Disconnected from server")
        print("Disconnected from server")

    def command_toggle(self):
        # toggle to take/give up command
        if self.is_commander:
            self.command(2)
        else:
            self.command(1)

    def getDialog(self):
        return self._dialog

    def sendAllCommands(self):
        """
        Used for when the gui is closed by user, sends all commands in the queue rapidly to make sure server sees
        them before quit
        :return: none
        """

        while not self.command_queue.empty():
            self.cycle()

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
            else:
                packet = None

            # update command status
            if packet is None:
                self.is_commander = False
            elif packet["commander"] is None:
                self.is_commander = False
            elif packet["commander"] == hashlib.sha256(self.clientid.encode('utf-8')).hexdigest():
                self.is_commander = True
            else:
                self.is_commander = False
            self.led.setChecked(self.is_commander)

            self.last_packet = packet
            return self.last_packet
        except (EOFError, ConnectionResetError):
            self.soft_disconnect()
            return None
        except Exception:
            self.soft_disconnect()
            traceback.print_exc()
            return None
