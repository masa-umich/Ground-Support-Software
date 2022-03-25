from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from overrides import overrides

from constants import Constants
from MathHelper import MathHelper
from object import BaseObject

"""
Class to handle all HeatEx objects and their functionality 
"""
# TODO: HeatEx need to be more similar to solenoids so the base object can be expanded
class HeatEx(BaseObject):

    object_name = "Heat Exchanger"

    def __init__(self, widget_parent: QWidget, position: QPointF, fluid: int, width: float = 40,
                 height: float = 18, name: str = "HeatEx",
                 scale: float = 1, serial_number: str = '',
                 long_name: str = 'Heat Exchanger', is_vertical: bool = True,
                 locked: bool = False, position_locked: bool = False, _id: int = None,
                 serial_number_label_pos: str = "Bottom", serial_number_label_local_pos: QPointF = QPointF(0, 0),
                 serial_number_label_font_size: float = 10, long_name_label_pos: str = "Top",
                 long_name_label_local_pos: QPointF = QPointF(0,0), long_name_label_font_size: float = 12,
                 long_name_label_rows: int = 1):
        """
        Initializer for HeatEx

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

    @overrides
    def draw(self):
        """
        Draws the Heat Exchanger icon on screen
        """

        # Draws the HeatEx outline
        path = QPainterPath()
        
        if self.is_vertical == False:
            path.moveTo(0,self.height/2)
            path.lineTo(self.width/5,self.height/2)
            path.lineTo(self.width*2/5,0)
            path.lineTo(self.width*3/5,self.height)
            path.lineTo(self.width*4/5,self.height/2)
            path.lineTo(self.width,self.height/2)

        else:
            path.moveTo(self.width/2,0)
            path.lineTo(self.width/2,self.height/5)
            path.lineTo(0,self.height*2/5)
            path.lineTo(self.width,self.height*3/5)
            path.lineTo(self.width/2,self.height*4/5)
            path.lineTo(self.width/2,self.height)
        

        path.translate(self.position.x(), self.position.y()) # Translate it into position
        self.widget_parent.painter.drawPath(path) # Draw Path
        

        super().draw()
