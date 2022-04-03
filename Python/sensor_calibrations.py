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
import json

"""
Updated Sensor Calibration Window as of Winter 2022 - Jacob Avery
"""


class RangesLayout(QGridLayout):
    """
    Handles each horizontal channel layout individually, so they can be updated without changing the others.
    """

    def __init__(self, parent=None):
        super().__init__()
        self.rangesItems = QHBoxLayout()
        self.parent = parent

        self.DropDownMenu = QComboBox()

        self.saveDisplayed = False

    def addRanges(self, channelNum):
        DropDownList = ("Voltage/Pressure Range", "Slope/Offset")

        self.DropDownMenu.addItems(DropDownList)
        self.DropDownMenu.wheelEvent = lambda event: None
        # print(self.DropDownMenu.currentText())

        self.addWidget(self.DropDownMenu, 1, 1)
        self.DropDownMenu.activated[str].connect(lambda x: self.updateRanges(x, channelNum))

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

        currentSlopeLabel = QLabel("Current Board Slope [mV/psi]: " + str(0))
        currentSlopeLabel.setStyleSheet('''QLabel {
                            color: rgb(0, 200, 0);
                        }''')

        currentOffsetLabel = QLabel("Current Board Offset [mV]: " + str(0))
        currentOffsetLabel.setStyleSheet('''QLabel {
                            color: rgb(0, 200, 0);
                        }''')

        self.addLayout(self.rangesItems, 1, 0)
        self.addWidget(currentSlopeLabel, 2, 0)
        self.addWidget(currentOffsetLabel, 3, 0)
        # print(self.rangesItems.itemAt(0).widget().text())

        incorrectValuesLabel = QLabel("")
        self.addWidget(incorrectValuesLabel, 4, 0)

        return self

    def updateRanges(self, text, channelNum):
        # print(text)

        self.parent.rangeLayoutList.pop(channelNum)

        if self.itemAt(5):
            self.itemAt(5).widget().deleteLater()

        self.saveDisplayed = True
        if channelNum not in self.parent.channelsEdited:
            self.parent.channelsEdited.append(channelNum)
        notSavedLabel = QLabel("Not Saved")
        notSavedLabel.setStyleSheet('''QLabel {
            color: rgb(210, 105, 30);
        }''')
        self.addWidget(notSavedLabel, 5, 0)

        if text == "Voltage/Pressure Range":
            self.DropDownMenu.setCurrentIndex(0)
            # Deletes the items in rangesItems
            for i in reversed(range(self.rangesItems.count())):
                self.rangesItems.itemAt(i).widget().deleteLater()

            self.rangesItems.addWidget(QLabel("Voltage Max [V]:"))
            voltageMax = QLineEdit()
            voltageMax.setValidator(QDoubleValidator())
            voltageMax.textChanged.connect(lambda x: self.textChanged(x, channelNum, "voltageMax"))
            voltageMax.setText(str(self.parent.voltagePressureGrid[channelNum][0]))
            self.rangesItems.addWidget(voltageMax)
            self.rangesItems.addWidget(QLabel("Voltage Min [V]:"))
            voltageMin = QLineEdit()
            voltageMin.setValidator(QDoubleValidator())
            voltageMin.textChanged.connect(lambda x: self.textChanged(x, channelNum, "voltageMin"))
            voltageMin.setText(str(self.parent.voltagePressureGrid[channelNum][1]))
            self.rangesItems.addWidget(voltageMin)
            self.rangesItems.addWidget(QLabel("Pressure Max [psi]:"))
            pressureMax = QLineEdit()
            pressureMax.setValidator(QDoubleValidator())
            pressureMax.textChanged.connect(lambda x: self.textChanged(x, channelNum, "pressureMax"))
            pressureMax.setText(str(self.parent.voltagePressureGrid[channelNum][2]))
            self.rangesItems.addWidget(pressureMax)

            # self.saveDisplayed = False

            self.addLayout(self.rangesItems, 1, 0)

        else:
            self.DropDownMenu.setCurrentIndex(1)
            # Deletes the items in rangesItems
            for i in reversed(range(self.rangesItems.count())):
                self.rangesItems.itemAt(i).widget().deleteLater()

            self.rangesItems.addWidget(QLabel("Slope [mV/psi]:"))
            slope = QLineEdit()
            slope.setValidator(QDoubleValidator())
            slope.textChanged.connect(lambda x: self.textChanged(x, channelNum, "slope"))
            slope.setText(str(self.parent.slopeOffsetGrid[channelNum][0]))
            self.rangesItems.addWidget(slope)
            self.rangesItems.addWidget(QLabel("Offset [mV]:"))
            offset = QLineEdit()
            offset.setValidator(QDoubleValidator())
            offset.textChanged.connect(lambda x: self.textChanged(x, channelNum, "offset"))
            offset.setText(str(self.parent.slopeOffsetGrid[channelNum][1]))
            self.rangesItems.addWidget(offset)

            # self.saveDisplayed = False

            self.addLayout(self.rangesItems, 1, 0)

        self.parent.rangeLayoutList.insert(channelNum, self)

    def textChanged(self, text, channel=-1, input="None"):
        if channel != -1:
            if input == "voltageMax":
                self.parent.voltagePressureGrid[channel] = (
                    text, self.parent.voltagePressureGrid[channel][1], self.parent.voltagePressureGrid[channel][2])
            elif input == "voltageMin":
                self.parent.voltagePressureGrid[channel] = (
                    self.parent.voltagePressureGrid[channel][0], text, self.parent.voltagePressureGrid[channel][2])
            elif input == "pressureMax":
                self.parent.voltagePressureGrid[channel] = (
                    self.parent.voltagePressureGrid[channel][0], self.parent.voltagePressureGrid[channel][1], text)
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
                self.addWidget(notSavedLabel, 5, 0)  # ignore highlights

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
        # print(parent.__class__)
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

        self.fileName = ''

        self.refreshTimer = QTimer(self)

        self.directionsLabelOpen = False

        # Vertical layout to hold channels
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
            dialog = QMessageBox.question(self, 'Confirmation',
                                          "There are unsaved changes. Are you sure you want to close?",
                                          QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if dialog == QtWidgets.QMessageBox.Yes:
                a0.accept()
                # print('close')
                # save to higher class to remember data once this window closes
                # doesn't remember after GUI closes though, need to save the data to a config file
                self.refreshTimer.deleteLater()

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
        else:
            self.refreshTimer.deleteLater()

    def printGrid(self):
        """
        prints the grid to the terminal for checking
        """

        print()
        print("Voltage/Pressure", "Slope/Offset")
        for i in range(len(self.voltagePressureGrid)):
            print(self.voltagePressureGrid[i], self.slopeOffsetGrid[i])

    def loadData(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Pressure Cal Configurations",
                                                  self.gui.workspace_path.removesuffix(
                                                      '/Configurations') + "/PressureCalConfigurations",
                                                  "JSON Files (*.json)",
                                                  options=options)
        if fileName:
            self.fileName = fileName
            with open(fileName, "r") as read_file:
                data = json.load(read_file)

            for i in data:
                # print(data[i])
                channel = data[i]
                # print(channel["Slope"])
                # print(channel["Offset"])
                try:
                    if (not isinstance(channel["Slope"], float) and not isinstance(channel["Slope"], int)) or \
                            (not isinstance(channel["Offset"], float) and not isinstance(channel["Offset"], int)):
                        self.window.statusBar().showMessage("Pressure Cal Configuration failed to open from " + fileName)
                        self.failLoadLabel.setText("At Least 1 Channel Failed to Load!! Check that File has float-point numbers")
                        return

                    #channelNum = int(i.removePrefix("Channel ")) # only works with python 3.9
                    channelNum = int(i[len("Channel "):]) #lazy works with <3.9 you can remove later


                    self.slopeOffsetGrid[channelNum] = (channel["Slope"], channel["Offset"])
                    self.rangeLayoutList[channelNum].updateRanges("Slope/Offset", channelNum)
                except:
                    if (not isinstance(channel["Vmax"], float) and not isinstance(channel["Vmax"], int)) or \
                            (not isinstance(channel["Vmin"], float) and not isinstance(channel["Vmin"], int)) or \
                            (not isinstance(channel["Pmax"], float) and not isinstance(channel["Pmax"], int)):
                        self.window.statusBar().showMessage(
                            "Pressure Cal Configuration failed to open from " + fileName)
                        self.failLoadLabel.setText("At Least 1 Channel Failed to Load!! Check that File has float-point numbers")
                        return

                    channelNum = int(i[len("Channel "):])  #int(i.removeprefix("Channel "))

                    self.voltagePressureGrid[channelNum] = (channel["Vmax"], channel["Vmin"], channel["Pmax"])
                    self.rangeLayoutList[channelNum].updateRanges("Voltage/Pressure Range", channelNum)

            self.window.statusBar().showMessage("Pressure Cal Configuration opened from " + fileName)
            self.failLoadLabel.setText("")

    def saveData(self, channels, slopes, offsets, Vmaxes, Vmins, Pmaxes, save_as=False):
        """
        Pulls up Save As dialog, saves data to designated file and sets filename field
        """
        if save_as:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getSaveFileName(self, 'Save Pressure Cal Configurations',
                                                      self.gui.workspace_path.removesuffix(
                                                          '/Configurations') + "/PressureCalConfigurations",
                                                      "JSON Files (*.json)", options=options)
            
        elif self.fileName:
            fileName = self.fileName
        else:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getSaveFileName(self, 'Save Pressure Cal Configurations',
                                                      self.gui.workspace_path.removesuffix(
                                                          '/Configurations') + "/PressureCalConfigurations",
                                                      "JSON Files (*.json)", options=options)
        if fileName:
            if fileName.find(".json") == -1:
                fileName = fileName + ".json"
            self.fileName = fileName

            data = {}
            # print(channels)

            for channelNum in channels:
                if slopes[channelNum] != 0:
                    data = {**data,
                            f"Channel {channelNum}":
                                {
                                    "Slope": slopes[channelNum],
                                    "Offset": offsets[channelNum],
                                }
                            }
                elif Vmaxes[channelNum] != 0:
                    data = {**data,
                        f"Channel {channelNum}":
                            {
                                "Vmax": Vmaxes[channelNum],
                                "Vmin": Vmins[channelNum],
                                "Pmax": Pmaxes[channelNum],
                            }
                    }

            with open(fileName, "w") as write_file:
                json.dump(data, write_file, indent="\t")

            # self.window.statusBar().showMessage("Pressure Cal Configuration saved to " + fileName)
        else:
            print("\nError with SaveData command. Most likely the user pressed 'cancel' in the save\n"
                  "dialog. (View sensor_calibrations.py saveData function for code)\n")
            self.unSavedLabel.setText("At Least 1 Channel Failed to Save!!")

    def calibrateSensorsWindow(self, action: QAction = None):
        """
        main function that handles everything with the calibration window
        """

        # Resets the values - most importantly the layout
        # Without this, the layout keeps appending itself and requires a reboot of the GUI
        # self.__init__(self.gui, self.gui.voltagePressureGrid, self.gui.slopeOffsetGrid)

        self.channel = action.text()
        # print(action)

        if action.text() == "Pressurization Controller":
            # receives the previous grid if there is one from the previous window
            self.__init__(self.gui, self.window, self.gui.PCvoltagePressureGrid, self.gui.PCslopeOffsetGrid)
            self.channel_count = 6
        elif action.text() == "Engine Controller":
            self.__init__(self.gui, self.window, self.gui.ECvoltagePressureGrid, self.gui.ECslopeOffsetGrid)
            self.channel_count = 20
        elif action.text() == "GSE Controller":
            self.__init__(self.gui, self.window, self.gui.GSEvoltagePressureGrid, self.gui.GSEslopeOffsetGrid)
            self.channel_count = 22

        self.refreshTimer.timeout.connect(lambda: self.get_calibrate_sensors(action.text()))
        self.refreshTimer.start(1000)

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

            self.voltagePressureGrid.append(("0", "0", "0"))
            self.slopeOffsetGrid.append(("0", "0"))

            rangeLayout = RangesLayout(parent=self)  # ignore

            ranges = rangeLayout.addRanges(x)

            self.rangeLayoutList.append(rangeLayout)

            self.verticalLayout.addWidget(label, 2 * x + 2, 0)
            self.verticalLayout.addLayout(ranges, 2 * x + 3, 0)

        # self.printGrid()

        # use self.voltagePressureGrid and self.slopeOffsetGrid to index into values when needed!

        # print(rangeLayout.rangesItems.itemAt(0).widget().text())

        end += 1  # not sure what this is for....I left it from the old code

        # scroll area
        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.dialog)

        # set initial window size
        self.scrollArea.setFixedHeight(800 * self.gui.pixel_scale_ratio[0])
        self.scrollArea.setFixedWidth(1200 * self.gui.pixel_scale_ratio[0])

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

        saveAs_button = QPushButton("Save As")
        saveAs_button.setFont(font)
        saveAs_button.setDefault(False)
        saveAs_button.setAutoDefault(False)
        saveAs_button.clicked.connect(lambda: self.send_sensor_calibrations(action.text(), True))
        saveAs_button.setFixedWidth(300 * self.gui.pixel_scale_ratio[0])

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

        # buttonLayout.addWidget(cancel_button)
        buttonLayout.addWidget(save_button)
        buttonLayout.addWidget(saveAs_button)
        # buttonLayout.addWidget(refresh_button)  # TODO: are the refresh and calculate buttons necessary?
        # buttonLayout.addWidget(calc_button)
        buttonsWidget = QWidget()
        buttonsWidget.setLayout(buttonLayout)

        self.verticalLayout.addLayout(buttonLayout, 1, 0)

        directionsLabel = QLabel("Directions:\n"
                                 "* Load pressure cal data using the load button or manually type in values\n"
                                 "into the input fields below.\n"
                                 "* Use the selection box to switch between voltage/pressure and slope/offset values\n"
                                 "depending on the board.\n"
                                 "* The save button will send the unsaved values to the board and save the configuration.\n"
                                 "* The save as button will bring up the save dialog if you wish to change the file to save to.")
        directionsLabel.setStyleSheet('''QLabel {
            color: rgb(200, 200, 0);
        }''')

        self.unSavedLabel = QLabel("At Least 1 Channel Failed to Save!!")
        self.unSavedLabel.setFont(font)
        self.unSavedLabel.setStyleSheet("""QLabel {
            color: rgb(200, 0, 0);
        }""")
        self.unSavedLabel.setText("")

        self.failLoadLabel = QLabel("At Least 1 Channel Failed to Load!! Check that File has float-point numbers")
        self.failLoadLabel.setFont(font)
        self.failLoadLabel.setStyleSheet("""QLabel {
            color: rgb(210, 105, 30);
        }""")
        self.failLoadLabel.setText("")

        self.differentValuesLabel = QLabel("At Least One Channel's Slope/Offset Values are Different From Board's")
        self.differentValuesLabel.setFont(font)
        self.differentValuesLabel.setStyleSheet("""QLabel {
            color: rgb(200, 0, 0);
        }""")
        self.differentValuesLabel.setText("")

        font.setPointSize(20 * self.gui.font_scale_ratio)
        directionsLabel.setFont(font)

        loadFileButton = QPushButton("Load Data")
        loadFileButton.setFixedWidth(150 * self.gui.pixel_scale_ratio[0])
        loadFileButton.clicked.connect(lambda: self.loadData())

        saveButton = QPushButton("save")
        saveButton.setFixedWidth(150 * self.gui.pixel_scale_ratio[0])
        saveButton.clicked.connect(lambda: self.send_sensor_calibrations(action.text()))

        headerLayout = QtWidgets.QGridLayout()
        headerLayout.addWidget(directionsLabel, 0, 0)
        headerLayout.addWidget(loadFileButton, 0, 1)
        headerLayout.addWidget(saveButton, 1, 1)
        headerLayout.addWidget(self.unSavedLabel, 1, 0)
        headerLayout.addWidget(self.failLoadLabel, 2, 0)
        headerLayout.addWidget(self.differentValuesLabel, 3, 0)

        self.verticalLayout.addLayout(headerLayout, 0, 0)

        # added the title to the correct window
        self.setWindowTitle("Sensor Calibrations: " + action.text())

        self.dialog.show()
        self.layout.addWidget(self.scrollArea)
        self.layout.addWidget(buttonsWidget)
        self.show()

    def get_calibrate_sensors(self, board_name):
        # print('receiving...')

        # packet = None
        # timeout = 0.5
        prefix = self.interface.getPrefix(board_name)
        # cmd_dict = {
        #     "function_name": "refresh_calibrations",
        #     "target_board_addr": self.interface.getBoardAddr(board_name),
        #     "timestamp": int(datetime.now().timestamp()),
        #     "args": []
        # }
        # self.client_dialog.client.command(3, cmd_dict)
        # while True:
        #    if time.time() > timeout:
        #        break
        # time.sleep(timeout)  # Wait for the refresh to finish

        # self.cal_packet = self.last_packet

        atLeastOne = False
        for channel in range(self.channel_count):
            try:
                slope = self.window.last_packet[prefix + "pt_cal_slope[" + str(channel) + "]"]
                offset = self.window.last_packet[prefix + "pt_cal_offset[" + str(channel) + "]"]
            except:
                #slope = float(self.rangeLayoutList[channel].itemAt(2).widget().text().removeprefix("Current Board Slope [mV/psi]: "))
                #offset = float(self.rangeLayoutList[channel].itemAt(3).widget().text().removeprefix("Current Board Offset [mV]: "))
                slope = slope = float(self.rangeLayoutList[channel].itemAt(2).widget().text()[len("Current Board Slope [mV/psi]: "):])
                offset = float(self.rangeLayoutList[channel].itemAt(3).widget().text()[len("Current Board Offset [mV]: "):])

                # testing
            # import random
            # slope = random.randint(0, 10)
            # offset = random.randint(100, 500)

            # self.rangeLayoutList[channel].itemAt(2).widget().setText("Current Board Slope [mV/psi]: " + str(slope))
            # self.rangeLayoutList[channel].itemAt(3).widget().setText("Current Board Offset [mV]: " + str(offset))

            # currentSlope = self.slopeOffsetGrid[channel][0]
            # currentOffset = self.slopeOffsetGrid[channel][1]

            try:
                if self.rangeLayoutList[channel].itemAtPosition(1, 1).widget().currentText() == 'Slope/Offset':
                    currentSlope = float(self.slopeOffsetGrid[channel][0])
                    currentOffset = float(self.slopeOffsetGrid[channel][1])
                else:
                    currentSlope = ((float(self.voltagePressureGrid[channel][0]) - float(
                        self.voltagePressureGrid[channel][1])) / float(self.voltagePressureGrid[channel][2])) * 1000
                    currentOffset = float(self.voltagePressureGrid[channel][1]) * 1000
            except:
                currentSlope = 0
                currentOffset = 0

            if (slope != float(currentSlope)) or (offset != float(currentOffset)):
                # print(f"Channel: {channel}'s slope/offset is different!")
                # print(slope, currentSlope, offset, currentOffset)
                try:
                    if self.rangeLayoutList[channel].itemAt(5).widget().text() == "Not Saved":
                        return
                except:
                    pass
                self.rangeLayoutList[channel].itemAt(4).widget().setText("Slope/Offset is different than Board's!!")
                self.rangeLayoutList[channel].itemAt(4).widget().setStyleSheet('''QLabel {
                                                            color: rgb(210, 30, 30);
                                    }''')
                self.differentValuesLabel.setText("At Least One Channel's Slope/Offset Values are Different From Board's")
                atLeastOne = True
            else:
                self.rangeLayoutList[channel].itemAt(4).widget().setText("")
                if not atLeastOne:
                    self.differentValuesLabel.setText("")

    def send_sensor_calibrations(self, board_name, save_as=False):
        """
        Send the Calibration Data specified in the window.
        Only sends the data from channels that have been updated
        """

        # print('sending...')

        # send calibration data
        if self.channelsEdited:

            channelsToBeSent = []

            for channel in self.channelsEdited:
                channelsToBeSent.append(channel)

            self.channelsEdited = []

            slopes = []
            offsets = []
            Vmaxes = []
            Vmins = []
            Pmaxes = []

            for _ in range(self.channel_count):
                slopes.append(0)
                offsets.append(0)
                Vmaxes.append(0)
                Vmins.append(0)
                Pmaxes.append(0)

            # print("Update Channels: ")
            # for channel in channelsToBeSent:
            #     print(channel[0])
            # print()

            for channel in channelsToBeSent:

                # self.rangeLayoutList[channel].itemAtPosition(1, 2).widget().currentText()

                # if not, then the user did not specify the needed values
                success = True

                if self.rangeLayoutList[channel].itemAtPosition(1, 1).widget().currentText() == 'Slope/Offset':

                    # Try function to determine if the user specified all values - if not, raise error
                    try:
                        # set values
                        slope = float(self.slopeOffsetGrid[channel][0])
                        offset = float(self.slopeOffsetGrid[channel][1])

                        slopes[channel] = slope
                        offsets[channel] = offset

                        print(f"Update Channel {channel}: slope = {slope}; offset = {offset}\n")

                        # send command
                        cmd_dict = {
                            "function_name": "set_pt_slope_offset",
                            "target_board_addr": self.interface.getBoardAddr(board_name),
                            "timestamp": int(datetime.now().timestamp()),
                            "args": [slope, offset]
                        }
                        self.window.client_dialog.client.command(3, cmd_dict)

                        # Stores Sent Values into Current Board Values - for testing
                        # self.rangeLayoutList[channel].itemAt(2).widget().setText("Current Board Slope [mV/psi]: " + str(slope))
                        # self.rangeLayoutList[channel].itemAt(3).widget().setText("Current Board Offset [mV]: " + str(offset))

                    except:  # error that user did not specify all values
                        print(f"Error with slope and offset command. Most likely an error with the input of the\n"
                              "sensor calibrations. Make sure to input all values for the slope and offset.\n"
                              "(View sensor_calibrations.py -> send_sensor_calibrations function for info)\n")
                        success = False

                else:

                    # Try function to determine if the user specified all values - if not, raise error
                    try:
                        # take Voltage Max, Min, and Pressure Max and calculate slope and offset
                        slope = ((float(self.voltagePressureGrid[channel][0]) - float(
                            self.voltagePressureGrid[channel][1])) / float(self.voltagePressureGrid[channel][2])) * 1000
                        offset = float(self.voltagePressureGrid[channel][1]) * 1000

                        self.slopeOffsetGrid[channel] = (slope, offset)

                        Vmaxes[channel] = float(self.voltagePressureGrid[channel][0])
                        Vmins[channel] = float(self.voltagePressureGrid[channel][1])
                        Pmaxes[channel] = float(self.voltagePressureGrid[channel][2])

                        print(f"Update Channel {channel}: slope = {slope}; offset = {offset}\n")

                        # send command
                        cmd_dict = {
                            "function_name": "set_pt_slope_offset",
                            "target_board_addr": self.interface.getBoardAddr(board_name),
                            "timestamp": int(datetime.now().timestamp()),
                            "args": [slope, offset]
                        }
                        self.window.client_dialog.client.command(3, cmd_dict)

                        # Stores Sent Values into Current Board Values - for testing
                        # self.rangeLayoutList[channel].itemAt(2).widget().setText("Current Board Slope [mV/psi]: " + str(slope))
                        # self.rangeLayoutList[channel].itemAt(3).widget().setText("Current Board Offset [mV]: " + str(offset))

                    except:  # error that user did not specify all values
                        print("\nError with slope and offset command. Most likely an error with the input of the\n"
                              "sensor calibrations. Make sure to input all values for the voltage and pressure.\n"
                              "(View sensor_calibrations.py send_sensor_calibrations function for info)\n")
                        success = False

                if success:  # remove the unsaved label from the individual channel
                    self.rangeLayoutList[channel].itemAt(5).widget().deleteLater()
                    self.rangeLayoutList[channel].saveDisplayed = False
                    self.unSavedLabel.setText("")
                else:  # replace the unsaved label with the failed to save label below for the individual channel
                    self.rangeLayoutList[channel].itemAt(5).widget().setText("FAILED TO SAVE!!!")
                    self.rangeLayoutList[channel].itemAt(5).widget().setStyleSheet('''QLabel {
                                            color: rgb(210, 30, 30);
                    }''')
                    self.unSavedLabel.setText("At Least 1 Channel Failed to Save!!")
                    self.channelsEdited.append(channel)  # raises the "are you sure" window if not saved correctly

            self.saveData(channelsToBeSent, slopes, offsets, Vmaxes, Vmins, Pmaxes, save_as=save_as)
            # self.printGrid()
