from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys
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

"""
This file contains the class to create the main window
"""
class SensorCalibrationDialog(QScrollArea): #LimitWindow
    def __init__(self, board):
        super().__init__()

        dialog = QDialog()
        Title = "Sensor Calibrations:" + board
        dialog.setWindowTitle(Title)
        layout = QtWidgets.QVBoxLayout()
        dialog.setLayout(layout)
        dialog.setWindowModality(Qt.ApplicationModal)
        Channel_settings = ["pt_cal_lower_voltage", "pt_cal_upper_voltage", "pt_cal_upper_pressure"]
        # Vertical layout to hold everything
        verticalLayout = QGridLayout(dialog)

        channel_count = 0

        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.default_font)
        font.setPointSize(14)# * self.gui.font_scale_ratio)

        if (board == "Pressurization Controller"):
            channel_count = 6
        elif (board == "Flight Computer"):
            print(board)
        elif (board == "Engine Controller"):
            channel_count = 20
        elif (board== "Recovery Controller"):
            print(board)
        elif (board == "GSE Controller"):
            channel_count = 22


        #self.lower_voltage = []
        #self.upper_voltage = []
        #self.upper_pressure = []

        end = 0
        for x in range(channel_count):
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

            #self.lower_voltage.append(lower_voltage_box)
            #self.upper_voltage.append(upper_voltage_box)
            #self.upper_pressure.append(upper_pressure_box)

            label = QLabel("PT Channel " + str(x))
            label.setFont(font)

            label_buffer = QLabel("              ")
            label1 = QLabel("Lower Voltage")
            label2 = QLabel("Upper Voltage")
            label3 = QLabel("Pressure Range")
            font.setPointSize(18)# * self.gui.font_scale_ratio)
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

            verticalLayout.addLayout(labelLayout, 2 * x + 1, 0)
            verticalLayout.addLayout(formLayout, 2 * x + 2, 0)
            # verticalLayout.setColumnStretch(x, 20)

            end = 2 * x + 2

        end += 1

        self.setBackgroundRole(QPalette.Dark)
        self.setWidgetResizable(True)
        #self.setFixedHeight(1000)  # * self.gui.pixel_scale_ratio[0])
        #elf.setFixedWidth(800)  # * self.gui.pixel_scale_ratio[0])
        self.setWidget(dialog)


        # Horizontal button layout
        buttonLayout = QHBoxLayout()
        # Create the buttons, make sure there is no default option, and connect to functions
        cancel_button = QPushButton("Cancel")
        cancel_button.setFont(font)
        cancel_button.setDefault(False)
        cancel_button.setAutoDefault(False)
        cancel_button.clicked.connect(lambda: self.done(1))
        cancel_button.setFixedWidth(125) #* self.gui.pixel_scale_ratio[0])  # Lazy way to make buttons not full width

        font.setPointSize(20)# * self.gui.font_scale_ratio)

        save_button = QPushButton("Save")
        save_button.setFont(font)
        save_button.setDefault(False)
        save_button.setAutoDefault(False)
        save_button.clicked.connect(lambda: print("lol"))
        save_button.setFixedWidth(300)# * self.gui.pixel_scale_ratio[0])

        refresh_button = QPushButton("Refresh")
        refresh_button.setFont(font)
        refresh_button.setDefault(False)
        refresh_button.setAutoDefault(False)
        refresh_button.clicked.connect(lambda: print("lol"))
        refresh_button.setFixedWidth(300)# * self.gui.pixel_scale_ratio[0])  # Lazy way to make buttons not full

        # buttonLayout.addWidget(cancel_button)
        buttonLayout.addWidget(save_button)
        buttonLayout.addWidget(refresh_button)

        verticalLayout.addLayout(buttonLayout, 0, 0)


    #def update_values(self, last_packet):
     #       self.level0.update_values(last_packet)
#
 #           if self._dual:
  #              self.level1.update_values(last_packet)
        #dialog.show()
        #self.scrollArea.show()
        # sys.exit(app.exec_())
        # self.show_window(scrollArea)

        #################################################
