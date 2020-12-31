from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants
from board import Board

from overrides import overrides


class ControlsSidebarWidget(QWidget):
    """
    Widget that contains relevant information while conducting a test
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.centralWidget = parent
        self.window = parent.window
        self.controlsWidget = self.centralWidget.controlsWidget
        self.gui = self.centralWidget.gui

        # Defines placement and size of control panel
        self.left = self.gui.screenResolution[0] - self.centralWidget.panel_width
        self.top = 0

        self.width = self.centralWidget.panel_width
        self.height = self.gui.screenResolution[1]
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Sets color of control panel
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Constants.MASA_Blue_color)
        self.setPalette(p)

        self.painter = QPainter()

        self.show()

        # Create the label that will hold the status label, displays what task is being performed
        title_font = QFont()
        title_font.setStyleStrategy(QFont.PreferAntialias)
        title_font.setFamily(Constants.monospace_font)
        title_font.setPointSizeF(48 * self.gui.font_scale_ratio)
        self.title_label = QLabel(self)
        self.title_label.setFont(title_font)
        self.title_label.setText("Avionics")
        self.title_label.setFixedHeight(75 * self.gui.pixel_scale_ratio[1])
        self.title_label.setFixedWidth(self.width)
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title_label.move(10 * self.gui.pixel_scale_ratio[0], 0)  # Nasty but makes it look more centered
        self.title_label.show()

        # Create dummy boards
        # TODO: Make this a dropdown
        # self.board = Board(self, "Flight Computer")
        # self.board.move(2, self.title_label.y() + self.title_label.height()+1)
        # self.board1 = Board(self, "Engine Controller")
        # self.board1.move(2, self.board.pos().y() + self.board.height())
        self.board2 = Board(self, "Pressurization Controller")
        self.board2.move(2, self.title_label.y() + self.title_label.height()+1)
        # self.board3 = Board(self, "Recovery Controller")
        # self.board3.move(2, self.board2.pos().y() + self.board.height())
        # self.board4 = Board(self, "GSE Controller")
        # self.board4.move(2, self.board3.pos().y() + self.board.height())

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
        pen.setWidth(Constants.line_width)
        pen.setColor(Constants.MASA_Beige_color)
        self.painter.setPen(pen)

        # Draw the bottom border on the widget
        path = QPainterPath()
        # path.moveTo(0, 75 * self.gui.pixel_scale_ratio[1]-1)  # Bottom left corner
        # path.lineTo(self.width, 75 * self.gui.pixel_scale_ratio[1]-1)  # Straight across

        path.moveTo(1, 0)
        path.lineTo(1, self.height)
        path.moveTo(1, 75 * self.gui.pixel_scale_ratio[1]-1)
        path.lineTo(self.width, 75 * self.gui.pixel_scale_ratio[1]-1)

        self.painter.drawPath(path)

        self.painter.end()