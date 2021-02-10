from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import sys
from datetime import datetime
import serial
import serial.tools.list_ports

from constants import Constants
from s2Interface import S2_Interface
from LedIndicatorWidget import LedIndicator

class AbortButton(QtWidgets.QDialog):
    def __init__(self, client):
        super().__init__()
        self.setWindowTitle("Abort Button Settings")
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.interface = S2_Interface()
        self.client = client
        self.ser = serial.Serial(port=None, baudrate=9600, timeout=1)
        self.port = None
        self.is_armed = False
        self.state = False # True is abort, False is no abort
        self.last_abort_time = 0

        # Board address selector
        self.board_selector = QtWidgets.QComboBox()
        self.layout.addWidget(self.board_selector)
        self.board_selector.addItems(Constants.boards)

        # Button enable toggle
        self.arming_button = QtGui.QPushButton("Enable Button")
        self.layout.addWidget(self.arming_button)
        self.arming_button.clicked.connect(self.arm_toggle)

        # Serial port connection box
        connection = QtGui.QGroupBox("Button Connection")
        self.layout.addWidget(connection)
        connection_layout = QtGui.QHBoxLayout()
        connection.setLayout(connection_layout)
        self.ports_box = QtGui.QComboBox()
        connection_layout.addWidget(self.ports_box)
        scanButton = QtGui.QPushButton("Scan")
        scanButton.clicked.connect(self.scan)
        connection_layout.addWidget(scanButton)
        connectButton = QtGui.QPushButton("Connect")
        connectButton.clicked.connect(self.connect)
        connection_layout.addWidget(connectButton)
        
        # Button state indicator light
        self.indicator = LedIndicator(self)
        self.indicator.setDisabled(True)  # Make the led non-clickable
        # Make the led red
        self.indicator.on_color_1 = QColor(255, 0, 0)
        self.indicator.on_color_2 = QColor(176, 0, 0)
        self.indicator.off_color_1 = QColor(28, 0, 0)
        self.indicator.off_color_2 = QColor(156, 0, 0)
        connection_layout.addWidget(self.indicator)
        
        # Scan for devices
        self.scan()

    def connect(self):
        # connect to serial port
        # TODO: replace print to console with something else
        self.port = str(self.ports_box.currentText())
        if self.ser.isOpen():
            self.ser.close()
        try:
            self.ser = serial.Serial(port=self.port, baudrate=9600, timeout=1)
            if not self.ser.isOpen():
                self.ser.open()
            print("Connection established on %s" % str(self.port))
        except Exception as e:
            print("Unable to connect to selected port ", e)

    def scan(self):
        # scan for com ports, populate dropdown
        self.ports = self.interface.scan()
        self.ports_box.clear()
        self.ports_box.addItems(self.ports)
    
    def get_addr(self):
        # function to get user selected board and retrieve address
        name = self.board_selector.currentText()
        return self.interface.getBoardAddr(name)
    
    def abort(self):
        # abort handler function
        cmd_dict = {
            "function_name": "set_state",
            "target_board_addr": self.get_addr(),
            "timestamp": int(datetime.now().timestamp()),
            "args": [3]
        }
        if self.client:
            self.client.command(3, cmd_dict)
    
    def arm_toggle(self):
        # toggle to enable use of button 
        # (mainly if you want to test if button works without calling an abort)
        if self.is_armed == False:
            self.is_armed = True
            self.arming_button.setText("Disable Button")
        else:
            self.is_armed = False
            self.arming_button.setText("Enable Button")
    
    def cycle(self):
        # Update function for button object
        if self.ser.isOpen(): # if button is connected
            try: # parse button state
                self.ser.reset_input_buffer() # flush buffer b/c button sends update faster than GUI reads it
                val = self.ser.readline().decode("utf-8")
                self.state = bool(int(val[0]))
            except:
                pass
        
        self.indicator.setChecked(self.state) # update state indicator

        if self.is_armed: # TODO: tune lockout time or come up with better method
            if datetime.now().timestamp() - self.last_abort_time > 3 and self.state: # lock out time of N seconds before sending command again
                print("Manual Abort Triggered!")
                self.abort() # trigger abort
                self.last_abort_time = datetime.now().timestamp() # reset lockout


if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    controller = AbortButton(None)
    
    timer = QtCore.QTimer()
    timer.timeout.connect(controller.cycle)
    timer.start(50) # in ms, 20hz
    
    controller.show()
    sys.exit(app.exec())

        