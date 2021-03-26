from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QRect

# color picker button based on: https://www.mfitzp.com/article/qcolorbutton-a-color-selector-tool-for-pyqt/
class ColorButton(QtWidgets.QPushButton):
    '''
    Custom Qt Widget to show a chosen color.

    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).    
    '''

    colorChanged = QtCore.pyqtSignal()

    def __init__(self, default_color="#FF0000", *args, **kwargs):
        super(ColorButton, self).__init__(*args, **kwargs)
        self.default_color = default_color
        self._color = self.default_color
        self.setMaximumWidth(32)
        self.pressed.connect(self.onColorPicker)
        self.setStyleSheet("background-color: %s;" % self._color)

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit()

        if self._color:
            self.setStyleSheet("background-color: %s;" % self._color)
        else:
            self.setStyleSheet("")

    def color(self):
        return self._color

    def onColorPicker(self):
        '''
        Show color-picker dialog to select color.

        Qt will use the native dialog by default.

        '''
        self.setStyleSheet("")
        dlg = QtWidgets.QColorDialog(self)
        
        if self._color:
            dlg.setCurrentColor(QtGui.QColor(self._color))

        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.setColor("#FF0000")

        return super(ColorButton, self).mousePressEvent(e)