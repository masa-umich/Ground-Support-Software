from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from overrides import overrides
from constants import Constants


class Board(QWidget):

    object_name = "Board"

    def __init__(self, parent):
        super().__init__(parent)
        self.controlsSidebarWidget = parent
        self.painter = QPainter()

        self.setGeometry(0,0,self.controlsSidebarWidget.width, 200)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Constants.MASA_Blue_color)
        self.setPalette(p)

        self.show()


    @overrides
    def paintEvent(self, e):
        """
        This event is called automatically in the background by pyQt. It is used to update the drawing on screen
        This function calls the objects own drawing methods to perform the actual drawing calculations
        """
        self.painter.begin(self)

        # This makes the objects onscreen more crisp
        self.painter.setRenderHint(QPainter.HighQualityAntialiasing)

        # Default pen qualities
        pen = QPen()
        pen.setWidth(Constants.line_width+1)
        pen.setColor(Constants.Board_color)
        self.painter.setBrush(QBrush(Constants.Board_color, Qt.BDiagPattern))
        self.painter.setPen(pen)

        # Draw the bottom border on the widget
        path = QPainterPath()
        # path.moveTo(0, 75 * self.gui.pixel_scale_ratio[1]-1)  # Bottom left corner
        # path.lineTo(self.width, 75 * self.gui.pixel_scale_ratio[1]-1)  # Straight across

        path.moveTo(100, 50)
        path.lineTo(100, 150)
        path.lineTo(250,150)
        path.lineTo(250,50)
        path.lineTo(100,50)

        self.painter.drawPath(path)

        # Default pen qualities
        pen = QPen()
        pen.setWidth(Constants.line_width+2)
        pen.setColor(Qt.black)
        self.painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))
        self.painter.setPen(pen)

        self.painter.drawEllipse(QPoint(125, 77),10,10)
        self.painter.drawEllipse(QPoint(159, 77), 10, 10)
        self.painter.drawEllipse(QPoint(191, 77), 10, 10)
        self.painter.drawEllipse(QPoint(225, 77), 10, 10)

        self.painter.drawEllipse(QPoint(125, 123), 10, 10)
        self.painter.drawEllipse(QPoint(159, 123), 10, 10)
        self.painter.drawEllipse(QPoint(191, 123), 10, 10)
        self.painter.drawEllipse(QPoint(225, 123), 10, 10)

        self.painter.end()