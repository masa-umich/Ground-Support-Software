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

    softwareAbortSoftArmedSignal = pyqtSignal(bool)

    def __init__(self, gui):
        super().__init__()
        self.setWindowTitle("Abort Button Settings")
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self._gui = gui
        self.interface = S2_Interface()
        self.ser = serial.Serial(port=None, baudrate=9600, timeout=1)
        self.port = None
        self.is_armed = False
        self.is_soft_armed = False
        self.state = False # True is abort, False is no abort
        self.last_state = False
        self.last_abort_time = datetime.now().timestamp()

        # Board address selector
        self.board_selector = QtWidgets.QComboBox()
        self.layout.addWidget(self.board_selector)
        self.board_selector.addItems(Constants.boards)

        # Button enable toggle
        self.arming_button = QtGui.QPushButton("Enable Hardware Button")
        self.layout.addWidget(self.arming_button)
        self.arming_button.clicked.connect(self.arm_toggle)

        # Software Button enable toggle
        self.soft_arming_button = QPushButton("Enable Software Button")
        self.layout.addWidget(self.soft_arming_button)
        self.soft_arming_button.clicked.connect(self.soft_arm_toggle)

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
            "args": [6]
        }
        # if self.client:
        self._gui.liveDataHandler.sendCommand(3, cmd_dict)
    
    def soft_arm_toggle(self):
        """Enables the software abort button that appears in the lower right corner of the sidebar
        """
        if not self.is_soft_armed:
            self.is_soft_armed = True
            self.softwareAbortSoftArmedSignal.emit(True)
            self.soft_arming_button.setText("Disable Software Button")
        else:
            self.softwareAbortSoftArmedSignal.emit(False)
            self.is_soft_armed = False
            self.soft_arming_button.setText("Enable Software Button")

    def arm_toggle(self):
        # toggle to enable use of button 
        # (mainly if you want to test if button works without calling an abort)
        if self.is_armed == False:
            self.is_armed = True
            #self.last_state = False # to ensure abort triggers if button already depressed
            #self.state = False
            self.arming_button.setText("Disable Hardware Button")
        else:
            self.is_armed = False
            self.arming_button.setText("Enable Hardware Button")
    
    def cycle(self):
        # Update function for button object
        if self.ser.isOpen(): # if button is connected
            try: # parse button state
                self.ser.reset_input_buffer() # flush buffer b/c button sends update faster than GUI reads it
                val = self.ser.readline().decode("utf-8")
                self.last_state = self.state
                self.state = bool(int(val[0]))
            except:
                pass
        
        self.indicator.setChecked(self.state) # update state indicator

        if self.is_armed: # TODO: tune lockout time or come up with better method
            if not self.last_state and self.state: # edge trigger
                print("Manual Abort Triggered!")
                self.abort() # trigger abort
            # if (datetime.now().timestamp() - self.last_abort_time < 2) and self.state: # periodic lockout
            #     print("Manual Abort Triggered!")
            #     self.abort() # trigger abort
            #     self.last_abort_time = datetime.now().timestamp()


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

        
