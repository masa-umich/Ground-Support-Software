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

        self.saveDisplayed = False

    def addRanges(self, channelNum):
        DropDownList = ("Voltage/Pressure Range", "Slope/Offset")

        DropDownMenu = QComboBox()
        DropDownMenu.addItems(DropDownList)
        DropDownMenu.wheelEvent = lambda event: None
        # print(DropDownMenu.currentText())

        self.addWidget(DropDownMenu, 1, 2)
        DropDownMenu.activated[str].connect(lambda x: self.updateRanges(x, channelNum))

        # Deletes the items in rangesItems
        for i in reversed(range(self.rangesItems.count())):
            self.rangesItems.itemAt(i).widget().deleteLater()

        self.rangesItems.addWidget(QLabel("Voltage Max [V]:"))
        voltageMax = QLineEdit()
        voltageMax.setValidator(QDoubleValidator())
        voltageMax.setText(self.parent.voltagePressureGrid[channelNum][0])
        voltageMax.textChanged.connect(lambda x: self.textChanged(x, channelNum, "voltageMax"))
        self.rangesItems.addWidget(voltageMax)

        self.rangesItems.addWidget(QLabel("Voltage Min [V]:"))
        voltageMin = QLineEdit()
        voltageMin.setValidator(QDoubleValidator())
        voltageMin.setText(self.parent.voltagePressureGrid[channelNum][1])
        voltageMin.textChanged.connect(lambda x: self.textChanged(x, channelNum, "voltageMin"))
        self.rangesItems.addWidget(voltageMin)

        self.rangesItems.addWidget(QLabel("Pressure Max [psi]:"))
        pressureMax = QLineEdit()
        pressureMax.setValidator(QDoubleValidator())
        pressureMax.setText(self.parent.voltagePressureGrid[channelNum][2])
        pressureMax.textChanged.connect(lambda x: self.textChanged(x, channelNum, "pressureMax"))
        self.rangesItems.addWidget(pressureMax)

        self.saveDisplayed = False

        self.addLayout(self.rangesItems, 1, 0)
        # print(self.rangesItems.itemAt(0).widget().text())

        return self

    def updateRanges(self, text, channelNum):
        # print(text)

        self.parent.rangeLayoutList.pop(channelNum)

        if self.itemAt(2):
            self.itemAt(2).widget().deleteLater()

        self.saveDisplayed = True
        if channelNum not in self.parent.channelsEdited:
            self.parent.channelsEdited.append(channelNum)
        notSavedLabel = QLabel("Not Saved")
        notSavedLabel.setStyleSheet('''QLabel {
            color: rgb(210, 105, 30);
        }''')
        self.addWidget(notSavedLabel, 2, 0)  # ignore highlights

        if text == "Voltage/Pressure Range":
            # Deletes the items in rangesItems
            for i in reversed(range(self.rangesItems.count())):
                self.rangesItems.itemAt(i).widget().deleteLater()

            self.rangesItems.addWidget(QLabel("Voltage Max [V]:"))
            voltageMax = QLineEdit()
            voltageMax.setValidator(QDoubleValidator())
            voltageMax.textChanged.connect(lambda x: self.textChanged(x, channelNum, "voltageMax"))
            voltageMax.setText(self.parent.voltagePressureGrid[channelNum][0])
            self.rangesItems.addWidget(voltageMax)
            self.rangesItems.addWidget(QLabel("Voltage Min [V]:"))
            voltageMin = QLineEdit()
            voltageMin.setValidator(QDoubleValidator())
            voltageMin.textChanged.connect(lambda x: self.textChanged(x, channelNum, "voltageMin"))
            voltageMin.setText(self.parent.voltagePressureGrid[channelNum][1])
            self.rangesItems.addWidget(voltageMin)
            self.rangesItems.addWidget(QLabel("Pressure Max [psi]:"))
            pressureMax = QLineEdit()
            pressureMax.setValidator(QDoubleValidator())
            pressureMax.textChanged.connect(lambda x: self.textChanged(x, channelNum, "pressureMax"))
            pressureMax.setText(self.parent.voltagePressureGrid[channelNum][2])
            self.rangesItems.addWidget(pressureMax)

            # self.saveDisplayed = False

            self.addLayout(self.rangesItems, 1, 0)

        else:
            # Deletes the items in rangesItems
            for i in reversed(range(self.rangesItems.count())):
                self.rangesItems.itemAt(i).widget().deleteLater()

            self.rangesItems.addWidget(QLabel("Slope [mV/psi]:"))
            slope = QLineEdit()
            slope.setValidator(QDoubleValidator())
            slope.textChanged.connect(lambda x: self.textChanged(x, channelNum, "slope"))
            slope.setText(self.parent.slopeOffsetGrid[channelNum][0])
            self.rangesItems.addWidget(slope)
            self.rangesItems.addWidget(QLabel("Offset [mV]:"))
            offset = QLineEdit()
            offset.setValidator(QDoubleValidator())
            offset.textChanged.connect(lambda x: self.textChanged(x, channelNum, "offset"))
            offset.setText(self.parent.slopeOffsetGrid[channelNum][1])
            self.rangesItems.addWidget(offset)

            # self.saveDisplayed = False

            self.addLayout(self.rangesItems, 1, 0)

        self.parent.rangeLayoutList.insert(channelNum, self)

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

            if not self.saveDisplayed:
                self.saveDisplayed = True
                if channel not in self.parent.channelsEdited:
                    self.parent.channelsEdited.append(channel)
                notSavedLabel = QLabel("Not Saved")
                notSavedLabel.setStyleSheet('''QLabel {
                    color: rgb(210, 105, 30);
                }''')
                self.addWidget(notSavedLabel, 2, 0)  # ignore highlights

            # print(text + ", from Channel: " + str(channel) + " " + input)
            # print("Voltage/Pressure Range: " + str(self.parent.voltagePressureGrid[channel]))
            # print("Slope/Offset Range: " + str(self.parent.slopeOffsetGrid[channel]))

        else:
            print('error with Channels: check "textChanged" function within sensor_calibrations.py')


class SensorCalibrationDialog(QtWidgets.QDialog):
    def __init__(self, parent, window, voltagePressureGrid=None, slopeOffsetGrid=None):
        super().__init__()
        # EC: 20
        # Press: 6
        # GSE controller: 22

        if slopeOffsetGrid is None:
            slopeOffsetGrid = []
        if voltagePressureGrid is None:
            voltagePressureGrid = []
        self.gui = parent
        print(parent.__class__)
        self.window = window
        self.interface = window.interface
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

        self.rangeLayoutList = []

        self.voltagePressureGrid = voltagePressureGrid
        self.slopeOffsetGrid = slopeOffsetGrid

        self.channelsEdited = []

    def closeEvent(self, a0):
        """
        if there are unsaved changes: ask whether the user actually wants to close the window
        """

        if self.channelsEdited:
            dialog = QMessageBox.question(self, 'Confirmation', "There are unsaved changes. Are you sure you want to close?",
                                          QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if dialog == QtWidgets.QMessageBox.Yes:
                a0.accept()
                print('close')
                # save to higher class to remember data once this window closes
                # doesn't remember after GUI closes though, need to save the data to a config file
                if self.channel == "Pressurization Controller":
                    self.gui.PCvoltagePressureGrid = self.voltagePressureGrid
                    self.gui.PCslopeOffsetGrid = self.slopeOffsetGrid
                elif self.channel == "Engine Controller":
                    self.gui.ECvoltagePressureGrid = self.voltagePressureGrid
                    self.gui.ECslopeOffsetGrid = self.slopeOffsetGrid
                elif self.channel == "GSE Controller":
                    self.gui.GSEvoltagePressureGrid = self.voltagePressureGrid
                    self.gui.GSEslopeOffsetGrid = self.slopeOffsetGrid
            else:
                a0.ignore()

    def printGrid(self):
        """
        prints the grid to the terminal for checking
        """

        print()
        print("Voltage/Pressure", "Slope/Offset")
        for i in range(len(self.voltagePressureGrid)):
            print(self.voltagePressureGrid[i], self.slopeOffsetGrid[i])

    # def deleteSave(self):
    #     """
    #     just a function to call to delete the save label after 3 seconds.
    #     """
    #     self.savedLabel.deleteLater()
    #     self.timer.deleteLater()

    def calibrateSensorsWindow(self, action: QAction = None):
        """
        main function that handles everything
        """

        # Resets the values - most importantly the layout
        # Without this, the layout keeps appending itself and requires a reboot of the GUI
        # self.__init__(self.gui, self.gui.voltagePressureGrid, self.gui.slopeOffsetGrid)

        self.channel = action.text()
        # print(action)

        if action.text() == "Pressurization Controller":
            # receives the previous grid if there is one from the previous window
            # TODO: still need to save this to a config file so that the data can be saved even after the GUI closes
            self.__init__(self.gui, self.window, self.gui.PCvoltagePressureGrid, self.gui.PCslopeOffsetGrid)
            self.channel_count = 6
        elif action.text() == "Engine Controller":
            self.__init__(self.gui, self.window, self.gui.ECvoltagePressureGrid, self.gui.ECslopeOffsetGrid)
            self.channel_count = 20
        elif action.text() == "GSE Controller":
            self.__init__(self.gui, self.window, self.gui.GSEvoltagePressureGrid, self.gui.GSEslopeOffsetGrid)
            self.channel_count = 22

        channel_settings = ["pt_cal_lower_voltage", "pt_cal_upper_voltage", "pt_cal_upper_pressure"]

        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.default_font)
        font.setPointSize(14 * self.gui.font_scale_ratio)

        end = 0
        # print(self.channel_count)
        for x in range(self.channel_count):
            """
            Iterates through and creates individual channels
            """
            font.setPointSize(18 * self.gui.font_scale_ratio)
            label = QLabel("\n\nPT Channel " + str(x))
            label.setFont(font)

            self.voltagePressureGrid.append(("", "", ""))
            self.slopeOffsetGrid.append(("", ""))

            rangeLayout = RangesLayout(parent=self)  # ignore

            ranges = rangeLayout.addRanges(x)

            self.rangeLayoutList.append(rangeLayout)

            self.verticalLayout.addWidget(label, 2 * x + 2, 0)  # ignore
            self.verticalLayout.addLayout(ranges, 2 * x + 3, 0)

        self.printGrid()

        """
        Old Code
        """
        # use self.voltagePressureGrid and self.slopeOffsetGrid to index into values when needed!

        # print(rangeLayout.rangesItems.itemAt(0).widget().text())

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

        end += 1  # not sure what this is for....I left it from the old code

        # scroll area
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


        # TODO: Directions...
        directionsLabel = QLabel("Directions: ...\n")

        # warning_label = QLabel("YOU MUST CLICK REFRESH TO MANUALLY REQUEST THE CURRENT CALS\n"
        #                        + "CALS TAKE A LONG TIME TO SAVE\n"
        #                        + "AFTER SAVING, KEEP CLICKING REFRESH UNTIL THE CORRECT VALUES APPEAR\n\n")
        # Fixed GUI Reboot Issue!

        directionsLabel.setStyleSheet('''QLabel {
            color: rgb(200, 200, 0);
        }''')

        font.setPointSize(20 * self.gui.font_scale_ratio)
        directionsLabel.setFont(font)
        warningLayout = QtWidgets.QGridLayout()
        warningLayout.addWidget(directionsLabel)

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

        # temporary
        if self.channelsEdited:

            channelsToBeSent = []

            for channel in self.channelsEdited:
                channelsToBeSent.append((channel, True))  # boolean value represents a successful/failed save. Replace
                                                          # with a real variable "sent back?" from transducers

            self.channelsEdited = []

            print("Update Channels: ")
            for channel in channelsToBeSent:
                print(channel[0])
            print()

            for channel, success in channelsToBeSent:
                if success:
                    self.rangeLayoutList[channel].itemAt(2).widget().deleteLater()
                    self.rangeLayoutList[channel].saveDisplayed = False

                    self.rangeLayoutList[channel].itemAtPosition(1, 2).widget().currentText()

                    # Send Here

                    if self.rangeLayoutList[channel].itemAtPosition(1, 2).widget().currentText() == 'Slope/Offset':
                        slope = float(self.slopeOffsetGrid[channel][0])
                        offset = float(self.slopeOffsetGrid[channel][1])

                        print(f"slope = {slope}")
                        print(f"offset = {offset}")

                        cmd_dict = {
                            "function_name": "set_pt_slope_offset",
                            "target_board_addr": self.interface.getBoardAddr(board_name),
                            "timestamp": int(datetime.now().timestamp()),
                            "args": [slope, offset]
                        }
                        self.window.client_dialog.client.command(3, cmd_dict)

                    else:

                        slope = ((float(self.voltagePressureGrid[channel][0]) - float(self.voltagePressureGrid[channel][1])) / float(self.voltagePressureGrid[channel][2])) * 1000
                        offset = float(self.voltagePressureGrid[channel][1]) * 1000

                        print(f"slope = {slope}")
                        print(f"offset = {offset}")

                        cmd_dict = {
                            "function_name": "set_pt_slope_offset",
                            "target_board_addr": self.interface.getBoardAddr(board_name),
                            "timestamp": int(datetime.now().timestamp()),
                            "args": [slope, offset]
                        }
                        self.window.client_dialog.client.command(3, cmd_dict)

                    # self.savedLabel = QLabel("Saved!")
                    # self.savedLabel.setStyleSheet('''QLabel {
                    #     color: rgb(0, 255, 0);
                    # }''')
                    # self.layout.addWidget(self.savedLabel)
                    #
                    # # deletes the save label 3 seconds after saving
                    # self.timer = QTimer(self)
                    # self.timer.timeout.connect(self.deleteSave)
                    # self.timer.start(3000)

                else:
                    self.rangeLayoutList[channel].itemAt(2).widget().setText("FAILED TO SAVE!!!")
                    self.rangeLayoutList[channel].itemAt(2).widget().setStyleSheet('''QLabel {
                        color: rgb(210, 30, 30);
                    }''')
                    self.channelsEdited.append(channel)

            self.printGrid()

            # TODO: talk to Jack about packet transmitting

        # temporary

        """
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
        """
