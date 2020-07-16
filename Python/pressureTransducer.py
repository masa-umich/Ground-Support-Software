from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from overrides import overrides
from constants import Constants
from object import BaseObject


class PressureTransducer(BaseObject):

    object_name = "Pressure Transducer"

    def __init__(self, widget_parent: QWidget, position: QPointF, fluid: int, width: float = 50*1,
                 height: float = 20*1, name: str = "PT",
                 scale: float = 1, avionics_number: int = 5, short_name: str = 'OX-SN-G07',
                 long_name: str = 'LOX Dewar Drain', is_vertical: bool = False,
                 locked: bool = False, position_locked: bool = False, _id: int = None,
                 short_name_label_pos: str = "Bottom", short_name_label_local_pos: QPoint = QPoint(0, 0),
                 short_name_label_font_size: float = 10, long_name_label_pos: str = "Top",
                 long_name_label_local_pos: QPoint = QPoint(0, 0), long_name_label_font_size: float = 23,
                 long_name_label_rows: int = 1):

        """
        Initializer for Solenoid

        :param widget_parent: parent widget
        :param position: position of icon on screen
        :param fluid: fluid in object
        :param width: width of object
        :param height: height of object
        :param name: name of object
        :param scale: scale applied to the object
        :param avionics_number: avionics identifier
        :param short_name: abbreviated name on schematics
        :param long_name: human-readable name for display on screen
        :param is_vertical: tracker if object is drawn vertically
        :param locked: tracker if the object is locked from editing
        :param position_locked: tracker if the object position is locked
        :param _id: unique internal gui id of the object
        :param short_name_label_pos: string of where the short name label is
        :param short_name_label_local_pos: local position on where short name label is
        :param short_name_label_font_size: font size of short name label
        :param long_name_label_pos: string of where the long name label is
        :param long_name_label_local_pos: local position on where long name label is
        :param long_name_label_font_size: font size of long name label
        :param long_name_label_rows: how many rows long name label should have
        """

        # Initialize base classes
        super().__init__(parent=widget_parent, position=position, fluid=fluid, width=width, height=height,
                         name=name, is_vertical=is_vertical, scale=scale, avionics_number=avionics_number,
                         short_name=short_name, long_name=long_name, locked=locked, position_locked=position_locked,
                         _id=_id, short_name_label_pos=short_name_label_pos,
                         short_name_label_local_pos=short_name_label_local_pos,
                         short_name_label_font_size=short_name_label_font_size,
                         long_name_label_pos=long_name_label_pos, long_name_label_local_pos=long_name_label_local_pos,
                         long_name_label_font_size=long_name_label_font_size,
                         long_name_label_rows=long_name_label_rows)

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
