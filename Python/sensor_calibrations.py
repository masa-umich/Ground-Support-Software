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
from flash import FlashDialog
from abort_button import AbortButton
from limits import LimitWindow
from auto_manager import AutoManager
from dp import TankLevelDialog

from overrides import overrides
import os
import ctypes
from datetime import datetime


class RangesLayout(QGridLayout):
    """
    Handles each horizontal channel layout individually, so they can be updated without changing the others.
    """

    def __init__(self, parent=None):
        super().__init__()
        self.rangesItems = QHBoxLayout()
        self.parent = parent

    def addRanges(self, channelNum):
        DropDownList = ("Voltage/Pressure Range", "Slope/Offset")

        DropDownMenu = QComboBox()
        DropDownMenu.addItems(DropDownList)
        DropDownMenu.wheelEvent = lambda event: None

        self.addWidget(DropDownMenu, 1, 2)
        DropDownMenu.activated[str].connect(lambda x: self.updateRanges(x, channelNum))

        # Deletes the items in rangesItems
        for i in reversed(range(self.rangesItems.count())):
            self.rangesItems.itemAt(i).widget().deleteLater()

        self.rangesItems.addWidget(QLabel("Voltage Max:"))
        voltageMax = QLineEdit()
        voltageMax.setValidator(QDoubleValidator())
        voltageMax.textChanged.connect(lambda x: self.textChanged(x, channelNum, "voltageMax"))
        self.rangesItems.addWidget(voltageMax)
        self.rangesItems.addWidget(QLabel("Voltage Min:"))
        voltageMin = QLineEdit()
        voltageMin.setValidator(QDoubleValidator())
        voltageMin.textChanged.connect(lambda x: self.textChanged(x, channelNum, "voltageMin"))
        self.rangesItems.addWidget(voltageMin)
        self.rangesItems.addWidget(QLabel("Pressure Max:"))
        pressureMax = QLineEdit()
        pressureMax.setValidator(QDoubleValidator())
        pressureMax.textChanged.connect(lambda x: self.textChanged(x, channelNum, "pressureMax"))
        self.rangesItems.addWidget(pressureMax)

        self.addLayout(self.rangesItems, 1, 0)

        return self

    def updateRanges(self, text, channelNum):
        # print(text)

        if text == "Voltage/Pressure Range":
            # Deletes the items in rangesItems
            for i in reversed(range(self.rangesItems.count())):
                self.rangesItems.itemAt(i).widget().deleteLater()

            self.rangesItems.addWidget(QLabel("Voltage Max:"))
            voltageMax = QLineEdit()
            voltageMax.setValidator(QDoubleValidator())
            voltageMax.textChanged.connect(lambda x: self.textChanged(x, channelNum, "voltageMax"))
            voltageMax.setText(self.parent.voltagePressureGrid[channelNum][0])
            self.rangesItems.addWidget(voltageMax)
            self.rangesItems.addWidget(QLabel("Voltage Min:"))
            voltageMin = QLineEdit()
            voltageMin.setValidator(QDoubleValidator())
            voltageMin.textChanged.connect(lambda x: self.textChanged(x, channelNum, "voltageMin"))
            voltageMin.setText(self.parent.voltagePressureGrid[channelNum][1])
            self.rangesItems.addWidget(voltageMin)
            self.rangesItems.addWidget(QLabel("Pressure Max:"))
            pressureMax = QLineEdit()
            pressureMax.setValidator(QDoubleValidator())
            pressureMax.textChanged.connect(lambda x: self.textChanged(x, channelNum, "pressureMax"))
            pressureMax.setText(self.parent.voltagePressureGrid[channelNum][2])
            self.rangesItems.addWidget(pressureMax)

            self.addLayout(self.rangesItems, 1, 0)

        else:
            # Deletes the items in rangesItems
            for i in reversed(range(self.rangesItems.count())):
                self.rangesItems.itemAt(i).widget().deleteLater()

            self.rangesItems.addWidget(QLabel("Slope:"))
            slope = QLineEdit()
            slope.setValidator(QDoubleValidator())
            slope.textChanged.connect(lambda x: self.textChanged(x, channelNum, "slope"))
            slope.setText(self.parent.slopeOffsetGrid[channelNum][0])
            self.rangesItems.addWidget(slope)
            self.rangesItems.addWidget(QLabel("Offset:"))
            offset = QLineEdit()
            offset.setValidator(QDoubleValidator())
            offset.textChanged.connect(lambda x: self.textChanged(x, channelNum, "offset"))
            offset.setText(self.parent.slopeOffsetGrid[channelNum][1])
            self.rangesItems.addWidget(offset)

            self.addLayout(self.rangesItems, 1, 0)

    def textChanged(self, text, channel=-1, input="None"):
        if channel != -1:
            if input == "voltageMax":
                self.parent.voltagePressureGrid[channel] = (text, self.parent.voltagePressureGrid[channel][1], self.parent.voltagePressureGrid[channel][2])
            elif input == "voltageMin":
                self.parent.voltagePressureGrid[channel] = (self.parent.voltagePressureGrid[channel][0], text, self.parent.voltagePressureGrid[channel][2])
            elif input == "pressureMax":
                self.parent.voltagePressureGrid[channel] = (self.parent.voltagePressureGrid[channel][0], self.parent.voltagePressureGrid[channel][1], text)
            elif input == "slope":
                self.parent.slopeOffsetGrid[channel] = (text, self.parent.slopeOffsetGrid[channel][1])
            elif input == "offset":
                self.parent.slopeOffsetGrid[channel] = (self.parent.slopeOffsetGrid[channel][0], text)

            print(text + ", from Channel: " + str(channel) + " " + input)
            print("Voltage/Pressure Range: " + str(self.parent.voltagePressureGrid[channel]))
            print("Slope/Offset Range: " + str(self.parent.slopeOffsetGrid[channel]))

        else:
            print('error with Channels: check "textChanged" function')


class SensorCalibrationDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__()
        # EC: 20
        # Press: 6
        # GSE controller: 22

        self.gui = parent
        self.scrollArea = None
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.slope = []
        self.offset = []
        self.upper_pressure = []
        self.channel_count = 0
        self.cal_packet = None
        self.channel_count = 0
        self.dialog = QDialog(self)
        self.formLayout = QGridLayout()

        # Vertical layout to hold everything
        self.verticalLayout = QGridLayout(self.dialog)

        self.voltagePressureGrid = []
        self.slopeOffsetGrid = []


    # def addRangeItems(self, text):
    #     print(text)

        # if text == "Voltage/Pressure Range":
        #     # Deletes the items in rangesItems
        #     for i in reversed(range(self.rangesItems.count())):
        #         self.rangesItems.itemAt(i).widget().deleteLater()
        #
        #     self.rangesItems.addWidget(QLabel("Voltage Max:"))
        #     voltageMaxSpin = QDoubleSpinBox()
        #     self.rangesItems.addWidget(voltageMaxSpin)
        #     self.rangesItems.addWidget(QLabel("Voltage Min:"))
        #     voltageMinSpin = QDoubleSpinBox()
        #     self.rangesItems.addWidget(voltageMinSpin)
        #     self.rangesItems.addWidget(QLabel("Pressure Max:"))
        #     pressureMaxSpin = QDoubleSpinBox()
        #     self.rangesItems.addWidget(pressureMaxSpin)
        #
        #     self.rangesLayout.addLayout(self.rangesItems)
        #
        # else:
        #     # Deletes the items in rangesItems
        #     for i in reversed(range(self.rangesItems.count())):
        #         self.rangesItems.itemAt(i).widget().deleteLater()
        #
        #     self.rangesItems.addWidget(QLabel("Slope:"))
        #     Slope = QDoubleSpinBox()
        #     self.rangesItems.addWidget(Slope)
        #     self.rangesItems.addWidget(QLabel("Offset:"))
        #     Offset = QDoubleSpinBox()
        #     self.rangesItems.addWidget(Offset)
        #
        #     self.rangesLayout.addLayout(self.rangesItems)

    def closeEvent(self, a0):
        print('close')

    def calibrateSensorsWindow(self, action: QAction):
        self.__init__(self.gui)  # Resets the values - most importantly the layout
                                 # Without this, the layout keeps appending itself and requires a reboot of the GUI

        channel_settings = ["pt_cal_lower_voltage", "pt_cal_upper_voltage", "pt_cal_upper_pressure"]

        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.default_font)
        font.setPointSize(14 * self.gui.font_scale_ratio)

        # TODO: does the "flight computer" and "recovery controller" have boards? If not, then should I remove them
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

        end = 0

        for x in range(self.channel_count):
            """
            Iterates through and creates individual channels
            """
            font.setPointSize(18 * self.gui.font_scale_ratio)
            label = QLabel("\n\nPT Channel " + str(x))
            label.setFont(font)

            rangeLayout = RangesLayout(parent=self)

            ranges = rangeLayout.addRanges(x)

            self.verticalLayout.addWidget(label, 2 * x + 2, 0)
            self.verticalLayout.addLayout(ranges, 2 * x + 3, 0)

            self.voltagePressureGrid.append(("", "", ""))
            self.slopeOffsetGrid.append(("", ""))

        # Old Code
        # for x in range(self.channel_count):
        #     # self.rangeList.append()
        #
        #     # Create the form layout that will hold the text box
        #     # self.formLayout = QGridLayout()
        #     # labelLayout = QGridLayout()
        #
        #     # font.setPointSize(18 * self.gui.font_scale_ratio)
        #
        #     # slope_box = QLabel("Slope: 0.0")
        #     # slope_box.setStyleSheet('''QLabel {
        #     #     color: rgb(80, 175, 255);
        #     # }''')
        #     # slope_box.setFont(font)
        #     #
        #     # offset_box = QLabel("Offset: 0.0")
        #     # offset_box.setStyleSheet('''QLabel {
        #     #     color: rgb(210, 105, 30);
        #     #     }''')
        #     # offset_box.setFont(font)
        #
        #     # font.setPointSize(12 * self.gui.font_scale_ratio)
        #
        #     # DropDownMenu = QComboBox()
        #     # DropDownList = ("Voltage/Pressure Range", "Slope/Offset")
        #     # DropDownMenu.addItems(DropDownList)
        #     #
        #     # self.formLayout.addWidget(DropDownMenu, 1, 2)
        #     # DropDownMenu.activated[str].connect(self.addRangeItems)
        #     # self.addRangeItems(DropDownList[0])
        #
        #     # pRangeLabel = QLabel("Pressure Min:")
        #     # pRangeLabel.setFont(font)
        #
        #     # pressureRange = QHBoxLayout()
        #     # pRange = QDoubleSpinBox()
        #     # pressureRange.addWidget(DropDownMenu)
        #     # pressureRange.addWidget(pRange)
        #
        #     # vRangeLabel = QLabel("Voltage Min/Max:    ")
        #     # vRangeLabel.setFont(font)
        #     # vRange1 = QDoubleSpinBox()
        #     # vRange2 = QDoubleSpinBox()
        #     #
        #     # voltageRange = QHBoxLayout()
        #     # voltageRange.addWidget(vRangeLabel)
        #     # voltageRange.addWidget(vRange1)
        #     # voltageRange.addWidget(vRange2)
        #
        #     # self.slope.append(slope_box)
        #     # self.offset.append(offset_box)
        #
        #     '''
        #     lower_voltage_box = QDoubleSpinBox()
        #     lower_voltage_box.setMaximum(9999)
        #     lower_voltage_box.setValue(0)
        #     lower_voltage_box.setDecimals(2)
        #
        #     upper_voltage_box = QDoubleSpinBox()
        #     upper_voltage_box.setMaximum(9999)
        #     upper_voltage_box.setValue(0)
        #     upper_voltage_box.setDecimals(2)
        #
        #     upper_pressure_box = QDoubleSpinBox()
        #     upper_pressure_box.setMaximum(9999)
        #     upper_pressure_box.setValue(0)
        #     upper_pressure_box.setDecimals(0)
        #
        #     self.lower_voltage.append(lower_voltage_box)
        #     self.upper_voltage.append(upper_voltage_box)
        #     self.upper_pressure.append(upper_pressure_box)
        #     '''
        #
        #     # font.setPointSize(18 * self.gui.font_scale_ratio)
        #     # label = QLabel("PT Channel " + str(x))
        #     # label.setFont(font)
        #     #
        #     # label_buffer = QLabel("              ")
        #     # labelLayout.addWidget(label_buffer, 1, 1)
        #
        #     """if x == 0:
        #         label_buffer = QLabel(" ")
        #         # label1 = QLabel("Slope")
        #         # label1.setStyleSheet('''QLabel {
        #         # color: rgb(80, 175, 255);
        #         # }''')
        #         #
        #         # label2 = QLabel("Offset")
        #         # label2.setStyleSheet('''QLabel {
        #         # color: rgb(210, 105, 30);
        #         # }''')
        #
        #         font.setPointSize(18 * self.gui.font_scale_ratio)
        #         label.setFont(font)
        #         # label1.setFont(font)
        #         # label2.setFont(font)
        #
        #         #labelLayout.addWidget(label_buffer, 0, 1)
        #         #labelLayout.addWidget(label1, 0, 2)
        #         #labelLayout.addWidget(label2, 0, 3)"""
        #
        #     # self.formLayout.addWidget(label, 0, 0)
        #     # self.formLayout.addWidget(label_buffer, 2, 0)
        #     # self.formLayout.addWidget(slope_box, 0, 3)
        #     # self.formLayout.addWidget(offset_box, 0, 4)
        #     # self.formLayout.addLayout(self.rangesLayout, 1, 0)
        #     # self.formLayout.addLayout(voltageRange, 2, 1)
        #     # self.formLayout.addWidget(label_buffer, 2, 0)
        #
        #     # verticalLayout.addLayout(labelLayout, 2 * x + 2, 0)
        #     # verticalLayout.addLayout(self.formLayout, 2 * x + 3, 0)
        #
        #     # end = 2 * x + 3

        end += 1

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.dialog)

        # set initial window size
        self.scrollArea.setFixedHeight(800 * self.gui.pixel_scale_ratio[0])
        self.scrollArea.setFixedWidth(1000 * self.gui.pixel_scale_ratio[0])

        self.scrollArea.setWidgetResizable(True)

        # Horizontal button layout
        buttonLayout = QHBoxLayout()
        # Create the buttons, make sure there is no default option, and connect to functions
        cancel_button = QPushButton("Cancel")
        cancel_button.setFont(font)
        cancel_button.setDefault(False)
        cancel_button.setAutoDefault(False)
        cancel_button.clicked.connect(lambda: self.dialog.done(1))
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

        calc_button = QPushButton("Calculate")
        calc_button.setFont(font)
        calc_button.setDefault(False)
        calc_button.setAutoDefault(False)
        calc_button.clicked.connect(lambda: self.calculate())  # TODO: update for actual calculate function
        calc_button.setFixedWidth(300 * self.gui.pixel_scale_ratio[0])

        #buttonLayout.addWidget(cancel_button)
        buttonLayout.addWidget(save_button)
        buttonLayout.addWidget(refresh_button)
        buttonLayout.addWidget(calc_button)
        buttonsWidget = QWidget()
        buttonsWidget.setLayout(buttonLayout)

        self.verticalLayout.addLayout(buttonLayout, 1, 0)

        warning_label = QLabel("YOU MUST CLICK REFRESH TO MANUALLY REQUEST THE CURRENT CALS\n"
                               + "CALS TAKE A LONG TIME TO SAVE\n"
                               + "AFTER SAVING, KEEP CLICKING REFRESH UNTIL THE CORRECT VALUES APPEAR\n\n")
        # Fixed GUI Reboot Issue (I think!)

        warning_label.setStyleSheet('''QLabel {
            color: rgb(200, 0, 0);
        }''')

        font.setPointSize(20 * self.gui.font_scale_ratio)
        warning_label.setFont(font)
        warningLayout = QtWidgets.QGridLayout()
        warningLayout.addWidget(warning_label)

        self.verticalLayout.addLayout(warningLayout, 0, 0)

        # added the title to the correct window
        self.setWindowTitle("Sensor Calibrations: " + action.text())

        self.dialog.show()
        self.layout.addWidget(self.scrollArea)
        self.layout.addWidget(buttonsWidget)
        self.show()

    def get_calibrate_sensors(self, board_name):
        print('receiving...')
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
        print('sending...')
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
