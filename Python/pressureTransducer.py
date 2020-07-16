from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from overrides import overrides
from constants import Constants
from object import BaseObject


class PressureTransducer(BaseObject):

    object_name = "Pressure Transducer"
    def __init__(self, widget_parent, position, fluid, isVertical):

        """
        Init the pressure transducer object
        :param widget_parent: widget this object will be added to
        :param position: position of icon on screen
        :param fluid: fluid in object
        :param isVertical: tracker if object is drawn vertically
        :return:
        """

        # Initialize base classes
        super().__init__(parent=widget_parent, position=position, fluid=fluid, width= 50, height = 20, name = "PT", is_vertical=isVertical, is_being_edited = False)

        # TODO: Grab height and width from csv file
        # TODO: Grab object scale from widget_parent

        self.pressure = 0
        self.pressure_label = QLabel(self.widget_parent)

        self._initPressureLabel()

    def _initPressureLabel(self):
        """
        Inits the pressure label
        :return:
        """
        self.pressure_label.setFixedSize(QSize(self.width, self.height))
        self.pressure_label.move(self.position.x(), self.position.y())
        self.pressure_label.setText(str(self.pressure) + "psi")
        self.pressure_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.pressure_label.setStyleSheet('color: white')

        # Get font and set it
        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily("Arial")
        font.setPointSize(12 * self.gui.font_scale_ratio)
        self.pressure_label.setFont(font)

        self.pressure_label.show()
        self.pressure_label.lower()

    def setPressure(self, pressure: float):
        """
        Set pressure of the PT
        :param pressure: new pressure
        """
        self.pressure = pressure
        self.pressure_label.setText(str(self.pressure)+"psi")

    @overrides
    def move(self, point: QPoint):
        """
        Move object to a new position
        :param point: point to move to
        """
        super().move(point)

        if self.position_locked == False and self.locked == False:
            self.pressure_label.move(point)

    @overrides
    def onClick(self):
        """
        Called when the PT is clicked
        """

        if not self.widget_parent.window.is_editing:
            self.setPressure(self.pressure + 200)

        super().onClick()

    @overrides
    def draw(self):
        """
        Draws the PT icon on screen
        """
        self.widget_parent.painter.setBrush(QColor(10,22,44,100))
        self.widget_parent.painter.drawRect(QRect(self.position.x(), self.position.y(), self.width, self.height))

        super().draw()

    @overrides
    def deleteSelf(self):
        """
        Delete itself
        """
        self.pressure_label.deleteLater()
        del self.pressure_label

        super().deleteSelf()
