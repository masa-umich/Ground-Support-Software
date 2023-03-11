from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from overrides import overrides

from constants import Constants
from MathHelper import MathHelper
from object import BaseObject

"""
Class to handle all Chamber objects and their functionality 
"""
# TODO: Chambers need to be more similar to solenoids so the base object can be expanded
class Chamber(BaseObject):

    object_name = "Chamber"

    def __init__(
        self,
        widget_parent: QWidget,
        position: QPointF,
        fluid: int = 4,
        width: float = 88 * 1,
        height: float = 170 * 1,
        name: str = "Chamber",
        scale: float = 1,
        serial_number: str = "RP-D2",
        long_name: str = "Arpulus Delus the Second",
        is_vertical: bool = True,
        locked: bool = False,
        position_locked: bool = False,
        _id: int = None,
        serial_number_label_pos: str = "Bottom",
        serial_number_label_local_pos: QPointF = QPointF(0, 0),
        serial_number_label_font_size: float = 10,
        long_name_label_pos: str = "Top",
        long_name_label_local_pos: QPointF = QPointF(0, 0),
        long_name_label_font_size: float = 12,
        long_name_label_rows: int = 1,
        long_name_visible: bool = True,
        serial_number_visible: bool = True,
    ):
        """
        Initializer for Solenoid

        :param widget_parent: parent widget
        :param position: position of icon on screen
        :param fluid: fluid in object
        :param width: width of object
        :param height: height of object
        :param name: name of object
        :param scale: scale applied to the object
        :param serial_number: abbreviated name on schematics
        :param long_name: human-readable name for display on screen
        :param is_vertical: tracker if object is drawn vertically
        :param locked: tracker if the object is locked from editing
        :param position_locked: tracker if the object position is locked
        :param _id: unique internal gui id of the object
        :param serial_number_label_pos: string of where the serial number label is
        :param serial_number_label_local_pos: local position on where serial number label is
        :param serial_number_label_font_size: font size of serial number label
        :param long_name_label_pos: string of where the long name label is
        :param long_name_label_local_pos: local position on where long name label is
        :param long_name_label_font_size: font size of long name label
        :param long_name_label_rows: how many rows long name label should have
        """

        ## Initialize underlying class
        super().__init__(
            parent=widget_parent,
            position=position,
            fluid=fluid,
            width=width,
            height=height,
            name=name,
            is_vertical=is_vertical,
            scale=scale,
            serial_number=serial_number,
            long_name=long_name,
            locked=locked,
            position_locked=position_locked,
            _id=_id,
            serial_number_label_pos=serial_number_label_pos,
            serial_number_label_local_pos=serial_number_label_local_pos,
            serial_number_label_font_size=serial_number_label_font_size,
            long_name_label_pos=long_name_label_pos,
            long_name_label_local_pos=long_name_label_local_pos,
            long_name_label_font_size=long_name_label_font_size,
            long_name_label_rows=long_name_label_rows,
            long_name_visible=long_name_visible,
            serial_number_visible=serial_number_visible,
        )

    @overrides
    def onClick(self):
        """
        When a Chamber is clicked this function is called
        This is really only useful for adding plots and
        selecting the Chamber for editing
        """
        super().onClick()

        # Tells widget painter to update screen
        self.widget_parent.update()

        # placeholder for future functionality
        print("Chamber object clicked")

    @overrides
    def draw(self):
        """
        Draws the chamber on the screen
        """
        path = QPainterPath()

        if self.is_vertical == True:
            path.moveTo(0, self.height)
            path.lineTo(self.width * 0.25, self.height * 0.75)
            path.lineTo(0, self.height / 2)
            path.lineTo(0, 0)
            path.lineTo(self.width, 0)
            path.lineTo(self.width, self.height / 2)
            path.lineTo(self.width * 0.75, self.height * 0.75)
            path.lineTo(self.width, self.height)

        elif self.is_vertical == False:
            path.moveTo(self.width, 0)
            path.lineTo(self.width * 0.75, self.height * 0.25)
            path.lineTo(self.width / 2, 0)
            path.lineTo(0, 0)
            path.lineTo(0, self.height)
            path.lineTo(self.width / 2, self.height)
            path.lineTo(self.width * 0.75, self.height * 0.75)
            path.lineTo(self.width, self.height)

        path.translate(
            self.position.x(), self.position.y()
        )  # Translate it into position
        self.widget_parent.painter.drawPath(path)  # Draw Path

        super().draw()
