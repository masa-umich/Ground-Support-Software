from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys
import time
from PyQt5 import QtGui, QtCore, QtWidgets

from controlsWidget import ControlsWidget
from controlsPanelWidget import ControlsPanelWidget
from controlsSidebarWidget import ControlsSidebarWidget
from missionWidget import MissionWidget
from constants import Constants
from ClientWidget import ClientWidget, ClientDialog
from data_viewer import DataViewerDialog
from s2Interface import S2_Interface
from abort_button import AbortButton
from limits import LimitWindow
from auto_manager import AutoManager
from dp import TankLevelDialog

from overrides import overrides
import os
import ctypes
from datetime import datetime


class SensorCalibrationDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__()
        # EC: 20
        # Press: 6
        # GSE controller: 22

        self.gui = parent
        self.scrollArea = None
        self.lower_voltage = []
        self.upper_voltage = []
        self.upper_pressure = []
        self.channel_count = 0
        self.cal_packet = None
        self.channel_count = 0

    def calibrateSensorsWindow(self, action: QAction):
        channel_settings = ["pt_cal_lower_voltage", "pt_cal_upper_voltage", "pt_cal_upper_pressure"]

        dialog = QDialog(self)

        # Vertical layout to hold everything
        verticalLayout = QGridLayout(dialog)

        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.default_font)
        font.setPointSize(14 * self.gui.font_scale_ratio)

        if action.text() == "Pressurization Controller":
            self.channel_count = 6
        elif action.text() == "Flight Computer":
            print(action.text())
        elif action.text() == "Engine Controller":
            self.channel_count = 20
        elif action.text() == "Recovery Controller":
            print(action.text())
        elif action.text() == "GSE Controller":
            self.channel_count = 22

        # probably make a global channel var to store all the calibrations to load in
        # or make a function to refresh the channels that passes in one setting/count at a time and call it here
        # ask how refresh channel works
        end = 0
        for x in range(self.channel_count):
            # Create the form layout that will hold the text box
            formLayout = QtWidgets.QGridLayout()
            labelLayout = QtWidgets.QGridLayout()

            lower_voltage_box = QDoubleSpinBox()
            lower_voltage_box.setMaximum(9999)
            lower_voltage_box.setValue(0)
            lower_voltage_box.setDecimals(2)

            upper_voltage_box = QDoubleSpinBox()
            upper_voltage_box.setMaximum(9999)
            upper_voltage_box.setValue(0)
            upper_voltage_box.setDecimals(2)

            upper_pressure_box = QDoubleSpinBox()
            upper_pressure_box.setMaximum(9999)
            upper_pressure_box.setValue(0)
            upper_pressure_box.setDecimals(0)

            self.lower_voltage.append(lower_voltage_box)
            self.upper_voltage.append(upper_voltage_box)
            self.upper_pressure.append(upper_pressure_box)

            label = QLabel("PT Channel " + str(x))
            label.setFont(font)

            label_buffer = QLabel("              ")
            label1 = QLabel("Lower Voltage")
            label2 = QLabel("Upper Voltage")
            label3 = QLabel("Pressure Range")
            font.setPointSize(18 * self.gui.font_scale_ratio)
            label.setFont(font)
            label1.setFont(font)
            label2.setFont(font)
            label3.setFont(font)

            labelLayout.addWidget(label_buffer, 0, 1)
            labelLayout.addWidget(label1, 0, 2)
            labelLayout.addWidget(label2, 0, 3)
            labelLayout.addWidget(label3, 0, 4)

            formLayout.addWidget(label, 0, 1)
            formLayout.addWidget(lower_voltage_box, 0, 2)
            formLayout.addWidget(upper_voltage_box, 0, 3)
            formLayout.addWidget(upper_pressure_box, 0, 4)

            verticalLayout.addLayout(labelLayout, 2 * x + 2, 0)
            verticalLayout.addLayout(formLayout, 2 * x + 3, 0)
            # verticalLayout.setColumnStretch(x, 20)

            end = 2 * x + 3

        end += 1

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(dialog)

        # set initial window size
        self.scrollArea.setMinimumHeight(800 * self.gui.pixel_scale_ratio[0])
        self.scrollArea.setMinimumWidth(1000 * self.gui.pixel_scale_ratio[0])

        self.scrollArea.setWidgetResizable(True)

        # added the title to the correct window
        self.scrollArea.setWindowTitle("Sensor Calibrations: " + action.text())

        # Horizontal button layout
        buttonLayout = QHBoxLayout()
        # Create the buttons, make sure there is no default option, and connect to functions
        cancel_button = QPushButton("Cancel")
        cancel_button.setFont(font)
        cancel_button.setDefault(False)
        cancel_button.setAutoDefault(False)
        cancel_button.clicked.connect(lambda: dialog.done(1))
        cancel_button.setFixedWidth(125 * self.gui.pixel_scale_ratio[0])  # Lazy way to make buttons not full width

        font.setPointSize(20 * self.gui.font_scale_ratio)

        save_button = QPushButton("Save")
        save_button.setFont(font)
        save_button.setDefault(False)
        save_button.setAutoDefault(False)
        save_button.clicked.connect(lambda: self.send_sensor_calibrations(action.text()))
        save_button.setFixedWidth(300 * self.gui.pixel_scale_ratio[0])

        refresh_button = QPushButton("Refresh")
        refresh_button.setFont(font)
        refresh_button.setDefault(False)
        refresh_button.setAutoDefault(False)
        refresh_button.clicked.connect(lambda: self.get_calibrate_sensors(action.text()))
        refresh_button.setFixedWidth(300 * self.gui.pixel_scale_ratio[0])  # Lazy way to make buttons not full

        # buttonLayout.addWidget(cancel_button)
        buttonLayout.addWidget(save_button)
        buttonLayout.addWidget(refresh_button)

        verticalLayout.addLayout(buttonLayout, 1, 0)

        warning_label = QLabel("YOU MUST CLICK REFRESH TO MANUALLY REQUEST THE CURRENT CALS\n" \
                               + "CALS TAKE A LONG TIME TO SAVE\n" \
                               + "AFTER SAVING, KEEP CLICKING REFRESH UNTIL THE CORRECT VALUES APPEAR\n\n" \
                               + "KNOWN BUG: THIS WINDOW ONLY WORKS ONCE\n" \
                               + "AFTER CLOSING, REBOOT GUI TO USE AGAIN")

        font.setPointSize(20 * self.gui.font_scale_ratio)
        warning_label.setFont(font)
        warningLayout = QtWidgets.QGridLayout()
        warningLayout.addWidget(warning_label)

        verticalLayout.addLayout(warningLayout, 0, 0)

        dialog.show()
        self.scrollArea.show()
        # sys.exit(app.exec_())
        # self.show_window(scrollArea)
        
    '''
    don't think the code below works!
    '''

    def get_calibrate_sensors(self, board_name):
        packet = None
        timeout = 0.5
        prefix = self.interface.getPrefix(board_name)
        cmd_dict = {
            "function_name": "refresh_calibrations",
            "target_board_addr": self.interface.getBoardAddr(board_name),
            "timestamp": int(datetime.now().timestamp()),
            "args": []
        }
        # self.client_dialog.client.command(3, cmd_dict)
        # while True:
        #    if time.time() > timeout:
        #        break
        time.sleep(timeout)  # Wait for the refresh to finish
        self.cal_packet = self.last_packet
        for x in range(self.channel_count):
            self.lower_voltage[x].setValue(self.last_packet[prefix + "pt_cal_lower_voltage[" + str(x) + "]"])
            self.upper_voltage[x].setValue(self.last_packet[prefix + "pt_cal_upper_voltage[" + str(x) + "]"])
            self.upper_pressure[x].setValue(self.last_packet[prefix + "pt_cal_upper_pressure[" + str(x) + "]"])

    def send_sensor_calibrations(self, board_name):
        timeout = 0.5
        prefix = self.interface.getPrefix(board_name)

        for x in range(self.channel_count):
            update_lower_voltage = True
            update_upper_voltage = True
            update_upper_pressure = True

            if (self.cal_packet != None):
                if (self.cal_packet[prefix + "pt_cal_lower_voltage[" + str(x) + "]"] == self.lower_voltage[
                    x].value()):
                    update_lower_voltage = False
                if (self.cal_packet[prefix + "pt_cal_upper_voltage[" + str(x) + "]"] == self.upper_voltage[
                    x].value()):
                    update_upper_voltage = False
                if (self.cal_packet[prefix + "pt_cal_upper_pressure[" + str(x) + "]"] == self.upper_pressure[
                    x].value()):
                    update_upper_pressure = False

            if update_lower_voltage:
                cmd_dict = {
                    "function_name": "set_pt_lower_voltage",
                    "target_board_addr": self.interface.getBoardAddr(board_name),
                    "timestamp": int(datetime.now().timestamp()),
                    "args": [x, self.lower_voltage[x].value()]
                }
                # self.client_dialog.client.command(3, cmd_dict)

            if update_upper_voltage:
                cmd_dict = {
                    "function_name": "set_pt_upper_voltage",
                    "target_board_addr": self.interface.getBoardAddr(board_name),
                    "timestamp": int(datetime.now().timestamp()),
                    "args": [x, self.upper_voltage[x].value()]
                }
                # self.client_dialog.client.command(3, cmd_dict)
            if update_upper_pressure:
                cmd_dict = {
                    "function_name": "set_pt_upper_pressure",
                    "target_board_addr": self.interface.getBoardAddr(board_name),
                    "timestamp": int(datetime.now().timestamp()),
                    "args": [x, self.upper_pressure[x].value()]
                }
                # self.client_dialog.client.command(3, cmd_dict)
