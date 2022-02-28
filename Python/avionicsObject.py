from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from constants import Constants
from object import BaseObject
from overrides import overrides


class AvionicsObject(BaseObject):

    def __init__(self, parent: QWidget, position: QPointF, fluid: int, width: float = 40 *1,
                 height: float = 28, name: str = "Solenoid",
                 scale: float = 1, serial_number: str = '',
                 long_name: str = 'Solenoid', is_vertical: bool = False,
                 locked: bool = False, position_locked: bool = False, _id: int = None,
                 serial_number_label_pos: str = "Bottom", serial_number_label_local_pos: QPointF = QPointF(0,0),
                 serial_number_label_font_size: float = 10, long_name_label_pos: str = "Top",
                 long_name_label_local_pos: QPointF = QPointF(0,0), long_name_label_font_size: float = 12,
                 long_name_label_rows: int = 1, channel: str = 'Undefined', board: str = 'Undefined',
                 long_name_visible:bool = True, serial_number_visible: bool = True):

        super().__init__(parent=parent, position=position, fluid=fluid, width=width, height=height,
                         name=name, is_vertical=is_vertical, scale=scale,
                         serial_number=serial_number, long_name=long_name,locked=locked,position_locked=position_locked,
                         _id=_id, serial_number_label_pos=serial_number_label_pos,
                         serial_number_label_local_pos=serial_number_label_local_pos,
                         serial_number_label_font_size=serial_number_label_font_size,
                         long_name_label_pos=long_name_label_pos,long_name_label_local_pos=long_name_label_local_pos,
                         long_name_label_font_size=long_name_label_font_size,
                         long_name_label_rows=long_name_label_rows, long_name_visible = long_name_visible,
                         serial_number_visible = serial_number_visible)

        self.avionics_board = board
        self.channel = channel
        self.avionics_board = board

    def setAvionicsBoard(self, board: str):
        """
        Sets the avionics board the object is connected to
        :param board: string name of board object is connected to
        """
        self.avionics_board = board

        self.central_widget.window.statusBar().showMessage(self.object_name + "(" + self.long_name + ")" + ": board set to " + board)

    def setChannel(self, channel: str):
        """
        Sets channel of object
        :param channel: channel of the object
        """
        self.channel = channel

        self.central_widget.window.statusBar().showMessage(self.object_name + "(" + self.long_name + ")" + ": channel set to " + channel)

    @overrides
    def objectStatusCheck(self):
        """
        Override from object class, see there for more details
        :return: See object class
        """

        if self.long_name == "Test":
            return 2, "Bruhhh"

        if self.avionics_board == "Undefined" or self.channel == "Undefined":
            return 1, self.long_name + "- No board and/or channel defined"

        return 0, ""

    @overrides
    def generateSaveDict(self):
        """
        Generates dict of data to save. Most of the work happens in the object class but whatever avionics specific
        info needs to be saved is added here.
        """

        # Gets the BaseObject data that needs to be saved
        super_dict = super().generateSaveDict()

        # Extra data the avionics object contains that needs to be saved
        save_dict = {
            "channel": self.channel,
            "board": self.avionics_board
        }

        # Update the super_dict under the solenoid entry with the solenoid specific data
        super_dict[self.object_name + " " + str(self._id)].update(save_dict)

        print(super_dict)

        return super_dict