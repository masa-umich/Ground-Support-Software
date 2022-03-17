from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from constants import Constants
from object import BaseObject
from overrides import overrides
from termcolor import colored

import bidict


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
                 long_name_visible: bool = True, serial_number_visible: bool = True):

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

        self.updateAvionicsMappings(self.getBoardChannelString())

    def setAvionicsBoard(self, board: str):
        """
        Sets the avionics board the object is connected to
        :param board: string name of board object is connected to
        """
        oldBoardChan = self.getBoardChannelString()

        self.avionics_board = board

        self.updateAvionicsMappings(oldBoardChan)

        self.gui.setStatusBarMessage(self.object_name + "(" + self.long_name + ")" + ": board set to " + board)

    def setChannel(self, channel: str):
        """
        Sets channel of object
        :param channel: channel of the object
        """

        oldBoardChan = self.getBoardChannelString()

        self.channel = channel

        self.updateAvionicsMappings(oldBoardChan)

        self.gui.setStatusBarMessage(self.object_name + "(" + self.long_name + ")" + ": channel set to " + channel)

    def setLongName(self, name):
        """
        Sets long name and label of object
        :param name: long_name of the object
        """
        old_name = self.long_name

        super().setLongName(name)

        succeeded = self.updateAvionicsMappings(self.getBoardChannelString())

        if not succeeded:
            super().setLongName(old_name)
            self.updateAvionicsMappings(self.getBoardChannelString())
            self.gui.setStatusBarMessage("Cannot update name to '" + name + "' as that name is already taken!", True)

    def updateAvionicsMappings(self, oldBoardChan: str):
        """
        This function keeps a bidirectional double dictionary (keyed both ways) up to date. It uses the below
        getBoardChannelString() function as the primary key, with the long name as the secondary key. This will get
        called on object creation and then any time the board, channel, or long name gets updated. To actually update
        the right key, the old key-value pair needs to be removed, hence the the old argument. In addition, to make sure
        that no duplicate keys are in the dict (two same channels present), the object id_ is appended to the start of
        the key. This function throws an error when two objects have the exact same longname so that is no longer
        allowed
        :param oldBoardChan: the getBoardChannelString() for the object before being updated to new name and channel/
                              board
        :return: False if it cannot update name due to duplication, true if it does
        """
        # If the old key is in the dict then update then pop (remove) it
        if str(self._id) + "_" + oldBoardChan in self.central_widget.controlsWidget.avionics_mappings:
            self.central_widget.controlsWidget.avionics_mappings.pop(str(self._id) + "_" + oldBoardChan)

        # Add new key value pair
        try:
            self.central_widget.controlsWidget.avionics_mappings[str(self._id) + "_" + self.getBoardChannelString()] = self.long_name
        except bidict.ValueDuplicationError:
            return False

        return True

    def getBoardChannelString(self):
        """
        Returns a string in the form boardprefix.channel. For example gse.pressure[1] or gse.3 for solenoids or others
        :return: string of above
        """

        if self.object_name == "Generic Sensor":
            return self.channel
        elif self.isAvionicsFullyDefined():
            return self.central_widget.window.interface.getPrefix(self.avionics_board) + Constants.object_prefix_map[self.object_name] + self.channel
        else:
            return "Undefined"

    def isAvionicsFullyDefined(self):
        """
        Returns true if the avionics object has both a board and channel defined
        :return: True for avionics object that has a channel and avionics board defined
        """
        if self.avionics_board == "Undefined" or self.channel == "Undefined":
            return False
        else:
            return True

    @overrides
    def objectStatusCheck(self):
        """
        Override from object class, see there for more details
        :return: See object class
        """
        status = 0
        text = ""

        if self.long_name == "Test":
            status = 2
            text = "Bruhhh"

        if status != 2 and not self.isAvionicsFullyDefined():
            status = 1
            text = self.long_name + "- No board and/or channel defined"

        self.setObjectStatusLight(status, text)

        return status, text

    def setObjectStatusLight(self, status, text):
        if status == 1:
            self.long_name_label.light.setIndicatorColor("Yellow")
            self.long_name_label.showStatusIndicator(True)
        elif status == 2:
            self.long_name_label.light.setIndicatorColor("Red")
            self.long_name_label.showStatusIndicator(True)
        else:
            self.long_name_label.showStatusIndicator(False)

        self.long_name_label.light.setToolTip(text)

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