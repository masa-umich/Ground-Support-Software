import sys
#import os
from datetime import datetime
from overrides import overrides

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
import pyqtgraph as pg

from constants import Constants
from s2Interface import S2_Interface



class FlashDialog(QtWidgets.QDialog):
    def __init__(self, client, gui=None):
        super().__init__()
        self.flash_controller = FlashController(client, gui)

        self.setWindowTitle("Flash Controller")
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.flash_controller)
        self.setLayout(self.layout)


class FlashController(QtWidgets.QWidget):
    def __init__(self, client, gui = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = S2_Interface()
        self.client = client
        self.gui = gui

        self.gui.campaign.dataPacketSignal.connect(self.updateFromDataPacket)

        # logo
        self.logo = QtGui.QLabel()
        pixmap = QtGui.QPixmap("Images/flash.png")
        #pixmap = pixmap.scaled(400, 400, QtCore.Qt.KeepAspectRatio)
        self.logo.setPixmap(pixmap)
        self.logo.setAlignment(QtCore.Qt.AlignCenter)

        self.board_selector = QtWidgets.QComboBox()
        self.file_selector = QtWidgets.QLineEdit()
        self.file_button = QtWidgets.QPushButton("Select")
        self.download_button = QtWidgets.QPushButton("Dump Flash")
        self.wipe_button = QtWidgets.QPushButton("Wipe Flash")
        self.start_button = QtWidgets.QPushButton("Start Logging")
        self.stop_button = QtWidgets.QPushButton("Stop Logging")

        self.rem_mem = QtWidgets.QLabel(self)
        rem_mem_font = QtGui.QFont()
        rem_mem_font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        rem_mem_font.setFamily(Constants.monospace_font)
        rem_mem_font.setPointSizeF(14 * self.gui.font_scale_ratio)
        self.rem_mem.setFont(rem_mem_font)
        self.rem_mem.setText("0000 kb")
        #self.rem_mem.setStyleSheet("color: black")

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.logo, 0, 0, 1, 2)
        self.layout.addWidget(self.board_selector, 1, 0, 1, 2)
        #self.layout.addWidget(self.file_selector, 2, 0, 1, 1)
        #self.layout.addWidget(self.file_button, 2, 1, 1, 1)
        self.layout.addWidget(self.download_button, 3, 0, 1, 2)
        self.layout.addWidget(self.wipe_button, 6, 0, 1, 2)
        self.layout.addWidget(self.start_button, 4, 0, 1, 2)
        self.layout.addWidget(self.stop_button, 5, 0, 1, 2)
        self.layout.addWidget(self.rem_mem, 2, 0, 1, 2)

        self.board_selector.addItems(Constants.boards)

        self.file_button.clicked.connect(self.select_file)
        self.download_button.clicked.connect(self.dump)
        self.wipe_button.clicked.connect(self.wipe)
        self.start_button.clicked.connect(self.start_logging)
        self.stop_button.clicked.connect(self.stop_logging)




    def select_file(self):
        options = QtWidgets.QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Select Dump File", "", "Text Files (*.csv);;All Files (*)", options=options)
        if filename:
            self.file_selector.setText(filename)

    def get_addr(self):
        name = self.board_selector.currentText()
        if name != "":
            return self.interface.getBoardAddr(name)
        else:
            self.showDialog("Select a board.")
            return -1

    def showDialog(self, msg):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Critical)
        msgBox.setText(msg)
        msgBox.setWindowTitle("Error")
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        return msgBox.exec()


    def dump(self):
        addr = self.get_addr()
        if addr != -1:
            self.client.command(5, addr)
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        msgBox.setText("It's normal if the server freezes up for a bit so do not close or restart. Patience, grasshopper.")
        msgBox.setWindowTitle("Notice!")
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec()

    def wipe(self):
        addr = self.get_addr()
        dialog = QtWidgets.QMessageBox.question(self, '', "Are you sure you want to wipe flash?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if addr != -1 & dialog == QtWidgets.QMessageBox.Yes :
            cmd_dict = {
                "function_name": "wipe_flash",
                "target_board_addr": addr,
                "timestamp": int(datetime.now().timestamp()),
                "args": []
            }
            self.client.command(3, cmd_dict)

    def stop_logging(self):
        addr = self.get_addr()
        if addr != -1:
            cmd_dict = {
                "function_name": "stop_logging",
                "target_board_addr": addr,
                "timestamp": int(datetime.now().timestamp()),
                "args": []
            }
            self.client.command(3, cmd_dict)

    def start_logging(self):
        addr = self.get_addr()
        if addr != -1:
            cmd_dict = {
                "function_name": "start_logging",
                "target_board_addr": addr,
                "timestamp": int(datetime.now().timestamp()),
                "args": []
            }
            self.client.command(3, cmd_dict)

    # @overrides
    # def update(self, last_packet):
    #     prefix = self.interface.getPrefix(self.board_selector.currentText())
    #     key = prefix + "flash_mem"
    #     if( key in last_packet.keys()):
    #         rem_mem = (134086656 - int(last_packet[prefix + "flash_mem"]))/1024
    #     else:
    #         rem_mem = 0
    #     self.rem_mem.setText("Bytes Used: %.2f kB" %rem_mem)

    @QtCore.pyqtSlot(object)
    def updateFromDataPacket(self, data_packet: dict):
        prefix = self.interface.getPrefix(self.board_selector.currentText())
        key = prefix + "flash_mem"
        if key in data_packet.keys():
            rem_mem = (134086656 - int(data_packet[prefix + "flash_mem"])) / 1024
        else:
            rem_mem = 0
        self.rem_mem.setText("Bytes Used: %.2f kB" % rem_mem)


if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    controller = FlashDialog(None)

    controller.show()
    sys.exit(app.exec())
