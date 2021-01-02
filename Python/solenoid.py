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

    def __init__(self, widget_parent: QWidget, position: QPointF, fluid: int, width: float = 40 *1,
                 height: float = 18 *1, name: str = "Solenoid",
                 scale: float = 1, serial_number: str = '',
                 long_name: str = 'Solenoid', is_vertical: bool = False,
                 locked: bool = False, position_locked: bool = False, _id: int = None,
                 serial_number_label_pos: str = "Bottom", serial_number_label_local_pos: QPoint = QPoint(0,0),
                 serial_number_label_font_size: float = 10, long_name_label_pos: str = "Top",
                 long_name_label_local_pos: QPoint = QPoint(0,0), long_name_label_font_size: float = 12,
                 long_name_label_rows: int = 1, channel: str = 'Undefined', board: str = 'Undefined'):

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
        :param channel: the specific channel the device is plugged into
        :param board: the avionics board the device is plugged into
        """

        # TODO: Still bleah, should have a way to rotate or something

        if is_vertical:
            super().__init__(parent=widget_parent, position=position, fluid=fluid, width=width, height=height,
                             name=name, is_vertical=is_vertical, scale=scale,
                             serial_number=serial_number, long_name=long_name,locked=locked,position_locked=position_locked,
                             _id=_id, serial_number_label_pos=serial_number_label_pos,
                             serial_number_label_local_pos=serial_number_label_local_pos,
                             serial_number_label_font_size=serial_number_label_font_size,
                             long_name_label_pos=long_name_label_pos,long_name_label_local_pos=long_name_label_local_pos,
                             long_name_label_font_size=long_name_label_font_size,
                             long_name_label_rows=long_name_label_rows)
        else:
            # Initialize base classes
            super().__init__(parent=widget_parent, position=position, fluid=fluid, width=width, height=height,
                             name=name, is_vertical=is_vertical, scale=scale,
                             serial_number=serial_number, long_name=long_name,locked=locked,position_locked=position_locked,
                             _id=_id, serial_number_label_pos=serial_number_label_pos,
                             serial_number_label_local_pos=serial_number_label_local_pos,
                             serial_number_label_font_size=serial_number_label_font_size,
                             long_name_label_pos=long_name_label_pos,long_name_label_local_pos=long_name_label_local_pos,
                             long_name_label_font_size=long_name_label_font_size,
                             long_name_label_rows=long_name_label_rows)


        # TODO: Grab object scale from widget_parent

        # State tracks whether the solenoid is open or closed
        self.state = 0
        self.channel = channel
        self.avionics_board = board

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
            path.lineTo(self.width, 0)  # Diag to upper right
            path.lineTo(self.width, self.height)  # Straight Up
            path.lineTo(0, 0)

        else:  # Draw vertically
            path.lineTo(self.width, 0)
            path.lineTo(0, self.height)
            path.lineTo(self.width, self.height)
            path.lineTo(0, 0)

        path.translate(self.position.x(), self.position.y())

        self.widget_parent.painter.drawPath(path)

        # path = QPainterPath()
        # if self.is_vertical == 0:
        #     path = QPainterPath()
        #     path.moveTo(2*self.width/7, 0)  # Top left corner
        #     #path.lineTo(0,self.height)  # Straight Down
        #     #path.lineTo(self.width, 0)  # Diag to upper right
        #     path.lineTo(5*self.width/7, self.height)  # Straight Up
        #     #path.lineTo(0, 0)
        #     path.moveTo(5 * self.width / 7, 0)
        #     path.lineTo(2*self.width / 7, self.height)  # Straight Up
        #     pen = self.widget_parent.painter.pen()
        #     pen.setWidth(Constants.line_width+2)
        #     pen.setColor(Constants.MASA_Maize_color)
        #     self.widget_parent.painter.setPen(pen)
        #     path.translate(self.position.x(), self.position.y())
        #
        #     self.widget_parent.painter.drawPath(path)
        #
        # pen = self.widget_parent.painter.pen()
        # self.widget_parent.painter.setPen(Qt.NoPen)
        # self.widget_parent.painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
        # self.widget_parent.painter.drawEllipse(QPoint(self.position.x() + self.width/2, self.position.y() + self.height/2-8), 3, 3)
        # self.widget_parent.painter.setPen(pen)

        self.widget_parent.painter.setBrush(Qt.NoBrush)

        super().draw()

        # This is debug, draws a box around the origin of object
        #self.widget_parent.painter.fillRect(QRectF(self.position.x(), self.position.y(), 7, 7),Constants.fluidColor[self.fluid])

    @overrides
    def onClick(self):
        """
        When a solenoid is clicked this function is called
        """

        super().onClick()

        if not self.widget_parent.parent.is_editing:
            # Toggle state of solenoid
            self.toggle()

        # Tells widget painter to update screen
        self.widget_parent.update()

    def setAvionicsBoard(self, board: str):
        """
        Sets the avionics board the object is connected to
        :param board: string name of board object is connected to
        """
        self.avionics_board = board

    def setChannel(self, channel: str):
        """
        Sets channel of object
        :param channel: channel of the object
        """
        self.channel = channel

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

    @overrides
    def generateSaveDict(self):
        """
        Generates dict of data to save. Most of the work happens in the object class but whatever solenoid specific
        info needs to be saved is added here.
        """

        # Gets the BaseObject data that needs to be saved
        super_dict = super().generateSaveDict()

        # Extra data the Solenoid contains that needs to be saved
        save_dict = {
            "channel": self.channel,
            "board": self.avionics_board
        }

        # Update the super_dict under the solenoid entry with the solenoid specific data
        super_dict[self.object_name + " " + str(self._id)].update(save_dict)

        return super_dict
