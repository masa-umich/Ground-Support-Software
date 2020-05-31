from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from overrides import overrides

from constants import Constants
from object import BaseObject


class Solenoid(BaseObject):
    """
    Class to handle all solenoid objects and their functionality
    """

    object_name = "Solenoid"

    def __init__(self, widget_parent: QWidget, position: QPointF, fluid: int, width: float = 40 * 1.75,
                 height: float = 18 * 1.75, name: str = "Solenoid",
                 scale: float = 1, avionics_number: int = 5, short_name: str = 'OX-SN-G07',
                 long_name: str = 'LOX Dewar Drain', is_vertical: bool = False,
                 locked: bool = False, position_locked: bool = False, _id: int = None,
                 short_name_label_pos: str = "Bottom", short_name_label_local_pos: QPoint = QPoint(0,0),
                 short_name_label_font_size: float = 10, long_name_label_pos: str = "Top",
                 long_name_label_local_pos: QPoint = QPoint(0,0), long_name_label_font_size: float = 23,
                 long_name_label_rows: int = 1):

        """
        Init the solenoid object
        :param widget_parent: widget this object will be added to
        :param position: position of icon on screen
        :param fluid: fluid in object
        :param isVertical: tracker if object is drawn vertically
        :return:
        """

        # TODO: Still bleah, should have a way to rotate or something
        if is_vertical:
            super().__init__(parent=widget_parent, position=position, fluid=fluid, width=width, height=height,
                             name=name, is_vertical=is_vertical, scale=scale, avionics_number = avionics_number,
                             short_name=short_name, long_name=long_name,locked=locked,position_locked=position_locked,
                             _id=_id, short_name_label_pos=short_name_label_pos,
                             short_name_label_local_pos=short_name_label_local_pos,
                             short_name_label_font_size=short_name_label_font_size,
                             long_name_label_pos=long_name_label_pos,long_name_label_local_pos=long_name_label_local_pos,
                             long_name_label_font_size=long_name_label_font_size,
                             long_name_label_rows=long_name_label_rows)
        else:
            # Initialize base classes
            super().__init__(parent=widget_parent, position=position, fluid=fluid, width=width, height=height,
                             name=name, is_vertical=is_vertical, scale=scale, avionics_number = avionics_number,
                             short_name=short_name, long_name=long_name,locked=locked,position_locked=position_locked,
                             _id=_id, short_name_label_pos=short_name_label_pos,
                             short_name_label_local_pos=short_name_label_local_pos,
                             short_name_label_font_size=short_name_label_font_size,
                             long_name_label_pos=long_name_label_pos,long_name_label_local_pos=long_name_label_local_pos,
                             long_name_label_font_size=long_name_label_font_size,
                             long_name_label_rows=long_name_label_rows)

        # TODO: Grab height and width from csv file
        # TODO: Grab object scale from widget_parent

        # State tracks whether the solenoid is open or closed
        self.state = 0

    @overrides
    def draw(self):
        """
        Draws the solenoid icon on screen
        """

        # Holds the path of lines to draw
        path = QPainterPath()

        # If solenoid is open color it in
        if self.state == 1:
            self.widget_parent.painter.setBrush(Constants.fluidColor[self.fluid])  # This function colors in a path

        # Move path to starting position
        path.moveTo(0, 0)  # Top left corner

        # = 0 -> Draw horizontally
        if self.is_vertical == 0:
            path.lineTo(0,self.height)  # Straight Down
            path.lineTo(self.width,0)  # Diag to upper right
            path.lineTo(self.width, self.height)  # Straight Up
            path.lineTo(0, 0)

            # TODO: Implement three way Solenoid
            # path.moveTo(self.width/2, self.height/2)
            # path.lineTo((self.width/2) - (self.height/2), (self.height/2) - (self.width /2))
            # path.lineTo((self.width/2) + (self.height/2), (self.height/2) - (self.width /2))
            # path.lineTo(self.width/2, self.height/2)
        else:  # Draw vertically
            path.lineTo(self.width, 0)
            path.lineTo(0, self.height)
            path.lineTo(self.width, self.height)
            path.lineTo(0, 0)


        path.translate(self.position.x(), self.position.y())

        self.widget_parent.painter.drawPath(path)

        self.widget_parent.painter.setBrush(0)

        super().draw()

        # This is debug, draws a box around the origin of object
        #self.widget_parent.painter.fillRect(QRectF(self.position.x(), self.position.y(), 7, 7),Constants.fluidColor[self.fluid])

    @overrides
    def onClick(self):
        """
        When a solenoid is clicked this function is called
        """

        super().onClick()

        if not self.widget_parent.window.is_editing:
            # Toggle state of solenoid
            self.toggle()

        # Tells widget painter to update screen
        self.widget_parent.update()

    def toggle(self):
        """
        Toggle the state of the solenoid
        """

        if self.state == 0:
            self.state = 1
            self.setToolTip_("State: Open")
        elif self.state == 1:
            self.state = 0
            self.setToolTip_("State: Closed")
        else:
            print("WARNING STATE OF SOLENOID " + str(self._id) + " IS NOT PROPERLY DEFINED")

    # There is currently no Solenoid specific data that needs to be persistent but if some ever does it goes here
    # @overrides
    # def generateSaveDict(self):
    #     """
    #     Generates dict of data to save. Most of the work happens in the object class but whatever solenoid specific
    #     info needs to be saved is added here.
    #     """
    #
    #     # Gets the BaseObject data that needs to be saved
    #     super_dict = super().generateSaveDict()
    #
    #     # Extra data the Solenoid contains that needs to be saved
    #     save_dict = {
    #         "state": self.state
    #     }
    #
    #     # Update the super_dict under the solenoid entry with the solenoid specific data
    #     super_dict['Solenoid'].update(save_dict)
    #
    #     return super_dict
