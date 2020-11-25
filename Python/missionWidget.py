from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants
from overrides import overrides

import math

"""
This file contains the class to create the main controls widget (where the P&ID is)
"""


class MissionWidget(QWidget):
    """
    Class that creates the Control Widget. This widget contains all the graphical representations of objects, that can
    also be interacted with
    """

    def __init__(self, parent=None):
        """
        Initialize the widget
        :param parent: parent of this widget, is the central widget
        """
        super().__init__(parent)

        # The usual references
        self.parent = parent
        self.centralWidget = parent
        self.controlsWidget = self.centralWidget.controlsWidget
        self.controlsPanelWidget = self.centralWidget.controlsPanelWidget
        self.window = self.centralWidget.window
        self.gui = self.centralWidget.parent

        # Set Geometry
        self.width = self.centralWidget.width - self.controlsPanelWidget.width
        self.height = 75 * self.gui.pixel_scale_ratio[1]
        self.left = 0
        self.top = 0
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.show()

        # Painter controls the drawing of everything on the widget
        self.painter = QPainter()

        # Set background color
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Constants.MASA_Blue_color)
        self.setPalette(p)

        # Create the label that will hold the MET counter
        self.MET_label = QLabel(self)
        MET_font = QFont()
        MET_font.setStyleStrategy(QFont.PreferAntialias)
        MET_font.setFamily(Constants.monospace_font)
        MET_font.setPointSizeF(48 * self.gui.font_scale_ratio)
        self.MET_label.setFont(MET_font)
        self.MET_label.setText("MET-00:00:00")
        self.MET_label.setFixedHeight(self.height)
        self.MET_label.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        self.move(self.left, self.top-5)  # Nasty but makes it look more centered
        self.MET_label.show()

        # Connect the MET label to the Run MET update function
        self.gui.run.updateMETSignal.connect(self.updateMETLabel)

        self.show()

    def updateMETLabel(self, MET_time):
        """
        This function is called to update the MET label, this function is connected to signal in run class
        :param MET_time: The MET time in milliseconds
        """
        # Convert to Qtime to allow for easier string creation
        qtime = QTime(0, 0, 0)  # Can't pass in directly because the initializer does not like secs above 59
        qtime = qtime.addSecs(math.floor(MET_time/1000.0))

        # Updating Label text
        self.MET_label.setText("MET-" + qtime.toString("hh:mm:ss"))

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
        path.moveTo(0, self.height-1)  # Bottom left corner
        path.lineTo(self.width, self.height-1)  # Straight across

        # Draw the vertical line to the right of MET
        path.moveTo(self.MET_label.pos().x() + self.MET_label.width() + 10, self.height-1)  # + 10 is a buffer space
        path.lineTo(self.MET_label.pos().x() + self.MET_label.width() + 10, 0)

        # Draw path and end
        self.painter.drawPath(path)
        self.painter.end()