from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QRect

class Switch(QtWidgets.QPushButton):
    """
    Switch widget
    modified from https://stackoverflow.com/questions/56806987/switch-button-in-pyqt
    """
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setMinimumWidth(82)
        self.setMinimumHeight(22)

    def paintEvent(self, event):
        label = "R" if self.isChecked() else "L"
        bg_color = Qt.darkGray

        radius = 15
        width = 40
        center = self.rect().center()

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.translate(center)
        painter.setBrush(Qt.lightGray)

        pen = QtGui.QPen(Qt.white)
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawRoundedRect(QRect(-width, -radius, 2*width, 2*radius), radius, radius)
        painter.setBrush(QtGui.QBrush(bg_color))
        sw_rect = QRect(-radius, -radius, width + radius, 2*radius)
        if not self.isChecked():
            sw_rect.moveLeft(-width)
        painter.drawRoundedRect(sw_rect, radius, radius)
        painter.drawText(sw_rect, Qt.AlignCenter, label)