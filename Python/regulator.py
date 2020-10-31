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
class Regulator(BaseObject):
    object_name = "Regulator"

    def __init__(self, widget_parent: QWidget, position: QPointF, fluid: int = 4, width: float = 40 * 1,
                 height: float = 36 * 1, name: str = "Regulator",
                 scale: float = 1, serial_number: str = '',
                 long_name: str = 'Regulator', is_vertical: bool = True,
                 locked: bool = False, position_locked: bool = False, _id: int = None,
                 serial_number_label_pos: str = "Bottom", serial_number_label_local_pos: QPoint = QPoint(0, 0),
                 serial_number_label_font_size: float = 10, long_name_label_pos: str = "Top",
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
        super().__init__(parent=widget_parent, position=position, fluid=fluid, width=width, height=height,
                         name=name, is_vertical=is_vertical, scale=scale,
                         serial_number=serial_number, long_name=long_name, locked=locked, position_locked=position_locked,
                         _id=_id, serial_number_label_pos=serial_number_label_pos,
                         serial_number_label_local_pos=serial_number_label_local_pos,
                         serial_number_label_font_size=serial_number_label_font_size,
                         long_name_label_pos=long_name_label_pos, long_name_label_local_pos=long_name_label_local_pos,
                         long_name_label_font_size=long_name_label_font_size,
                         long_name_label_rows=long_name_label_rows)

        self.setAnchorPoints()

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
        print("Regulator object clicked")

    @overrides
    def draw(self):
        """
        Draws the chamber on the screen
        """
        path = QPainterPath()

        # If ThrottleValve is open color it in
        self.widget_parent.painter.setBrush(Constants.BG_color)


        if self.is_vertical == 0:  # Draw horizontally
            # Move path to starting position
            path.moveTo(0, self.height/2)
            path.lineTo(0, self.height)
            path.lineTo(self.width, self.height/2)
            path.lineTo(self.width, self.height)
            path.lineTo(0, self.height/2)
            Diam = self.height * 0.375
            path.moveTo(self.width/2, 0)
            path.lineTo(self.width/2, (3*self.height/2 - Diam)/2)
            path.lineTo(3*self.width/4, 0)
            path.lineTo(self.width/2, 0)

        else:  # Draw vertically
            path.lineTo(self.width, 0)
            path.lineTo(0, self.height)
            path.lineTo(self.width, self.height)
            path.lineTo(0, 0)
            Diam = self.width * 0.75
            path.moveTo(self.height, self.width / 2)
            path.lineTo(self.height - (3 * self.height / 2 - Diam) / 2, self.width / 2)
            path.lineTo(self.height, 3 * self.width / 4)
            path.lineTo(self.height, self.width / 2)

        # Draws "solenoid" shape with current brush
        path.translate(self.position.x(), self.position.y())
        self.widget_parent.painter.drawPath(path)

        # Draws ball shape overtop of solenoid shape
        path = QPainterPath()
        path.addEllipse((self.width - Diam) / 2, (3*self.height/2 - Diam) / 2, Diam, Diam)
        path.translate(self.position.x(), self.position.y())
        self.widget_parent.painter.drawPath(path)

        self.widget_parent.painter.setBrush(0)

        super().draw()


    @overrides
    def setAnchorPoints(self):
        """
        Sets the anchor points for the object. Called when object is created, and when scale changes
        """
        if self.is_vertical == False:
            self.anchor_points[0].updateLocalPosition(QPoint(0,int(3*self.height/4)))
            self.anchor_points[1].updateLocalPosition(QPoint(self.width ,int(3*self.height/4)))
            self.anchor_points[2].updateLocalPosition(QPoint(self.width/2,0))
            self.anchor_points[3].updateLocalPosition(QPoint(self.width/2, self.height))
        else:
            self.anchor_points[0].updateLocalPosition(QPoint(int(self.width/2),0))
            self.anchor_points[1].updateLocalPosition(QPoint(int(self.width/2),self.height))
            self.anchor_points[2].updateLocalPosition(QPoint(0,int(3*self.height/4)))
            self.anchor_points[3].updateLocalPosition(QPoint(self.width, int(3*self.height/4)))