from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from datetime import datetime
from overrides import overrides

from constants import Constants
#from object import BaseObject
from anchorPoint import AnchorPoint
from avionicsObject import AvionicsObject


class Solenoid(AvionicsObject):
    """
    Class to handle all solenoid objects and their functionality
    """

    object_name = "Solenoid"

    def __init__(self, widget_parent: QWidget, position: QPointF, fluid: int, width: float = 40 *1,
                 height: float = 28, name: str = "Solenoid",
                 scale: float = 1, serial_number: str = '',
                 long_name: str = 'Solenoid', is_vertical: bool = False,
                 locked: bool = False, position_locked: bool = False, _id: int = None,
                 serial_number_label_pos: str = "Bottom", serial_number_label_local_pos: QPointF = QPointF(0,0),
                 serial_number_label_font_size: float = 10, long_name_label_pos: str = "Top",
                 long_name_label_local_pos: QPointF = QPointF(0,0), long_name_label_font_size: float = 12,
                 long_name_label_rows: int = 1, channel: str = 'Undefined', board: str = 'Undefined',
                 normally_open: bool = 0, long_name_visible:bool = True, serial_number_visible:bool = True):

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

        super().__init__(parent=widget_parent, position=position, fluid=fluid, width=width, height=height,
                         name=name, is_vertical=is_vertical, scale=scale,
                         serial_number=serial_number, long_name=long_name,locked=locked,position_locked=position_locked,
                         _id=_id, serial_number_label_pos=serial_number_label_pos,
                         serial_number_label_local_pos=serial_number_label_local_pos,
                         serial_number_label_font_size=serial_number_label_font_size,
                         long_name_label_pos=long_name_label_pos,long_name_label_local_pos=long_name_label_local_pos,
                         long_name_label_font_size=long_name_label_font_size,
                         long_name_label_rows=long_name_label_rows, long_name_visible = long_name_visible,
                         serial_number_visible = serial_number_visible, board=board, channel=channel)


        # TODO: Grab object scale from widget_parent

        # State tracks whether the solenoid is open or closed
        self.state = 0
        self.voltage = 0
        self.current = 0
        self.normally_open = bool(normally_open)

        self.updateToolTip()

        self.gui.liveDataHandler.dataPacketSignal.connect(self.updateFromDataPacket)

    # TODO: Use this withe new configuration manager
    # @classmethod
    # def initFromObject(cls, object):

    @overrides
    def _initAnchorPoints(self):
        """
        Inits the anchor points for the object
        Should only be called from __init__
        Overridden because we don't want all four sides to have anchor points
        """
        # Default points are the midpoints of the four sides.
        coil_height = 10 # im sorry
        sol_mid_point = (self.height-coil_height)/2 + coil_height
        anchor_points = [AnchorPoint(QPoint(0, int(sol_mid_point)), self, 0, parent=self.widget_parent),
                         AnchorPoint(QPoint(self.width, int(sol_mid_point)), self, 1, parent=self.widget_parent),
                         AnchorPoint(QPoint(int(self.width/2 +1), int(sol_mid_point)), self, 2, parent=self.widget_parent)
                         ]
        self.anchor_points = anchor_points

    @overrides
    def draw(self):
        """
        Draws the solenoid icon on screen
        """
        # Holds the path of lines to draw
        path = QPainterPath()

        # If solenoid is normally closed and energized color it in, or if it is NO and de-energized
        if self.state == 1 and self.normally_open is False:
            self.widget_parent.painter.setBrush(Constants.fluidColor[self.fluid])  # This function colors in a path
        elif self.state == 0 and self.normally_open is True:
            self.widget_parent.painter.setBrush(Constants.fluidColor[self.fluid])
        else:
            self.widget_parent.painter.setBrush(Qt.NoBrush)

        # = 0 -> Draw horizontally
        if self.is_vertical is False:
            coil_height = 10 * self.gui.pixel_scale_ratio[1]
            sol_height = self.height - coil_height

            # Move path to starting position
            path.moveTo(0, coil_height)  # Top left corner of solenoid

            path.lineTo(0,self.height)  # Straight Down
            path.lineTo(self.width, coil_height)  # Diag to upper right
            path.lineTo(self.width, self.height)  # Straight Up
            path.lineTo(0, coil_height)

            path.translate(self.position.x(), self.position.y())
            self.widget_parent.painter.drawPath(path)
            path = QPainterPath()

            if self.state == 1:
                self.widget_parent.painter.setBrush(Constants.fluidColor[self.fluid])
            else:
                self.widget_parent.painter.setBrush(Qt.NoBrush)

            path.moveTo(self.width/2, coil_height + sol_height/2)
            path.lineTo(self.width/2, sol_height/2)
            path.addRect(self.width/3, 0, self.width/3, coil_height)  # left cord, width height

        else:  # Draw vertically
            coil_width = 10 * self.gui.pixel_scale_ratio[1]
            sol_width = self.width - coil_width

            path.moveTo(0, 0)
            path.lineTo(sol_width, 0)
            path.lineTo(0, self.height)
            path.lineTo(sol_width, self.height)
            path.lineTo(0, 0)

            path.translate(self.position.x(), self.position.y())
            self.widget_parent.painter.drawPath(path)
            path = QPainterPath()

            if self.state == 1:
                self.widget_parent.painter.setBrush(Constants.fluidColor[self.fluid])
            else:
                self.widget_parent.painter.setBrush(Qt.NoBrush)

            path.moveTo(sol_width/2, self.height/2)
            path.lineTo(sol_width/2 + coil_width, self.height/2)
            path.addRect(sol_width/2 + coil_width, self.height/3, coil_width, self.height/3) #left cord, width height

        path.translate(self.position.x(), self.position.y())

        self.widget_parent.painter.drawPath(path)

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

            if self.gui.debug_mode == False:
                # Toggle state of solenoid
                if self.state == 0:
                    new_state = 1
                elif self.state == 1:
                    new_state = 0
                if self.avionics_board != "Undefined" and self.channel != "Undefined":
                    cmd_dict = {
                        "function_name": "set_vlv",
                        "target_board_addr": self.widget_parent.window.interface.getBoardAddr(self.avionics_board),
                        "timestamp": int(datetime.now().timestamp()),
                        "args": [int(self.channel), int(new_state)]
                    }
                    #print(cmd_dict)
                    self.gui.liveDataHandler.sendCommand(3, cmd_dict)
            else:
                self.toggle()

        # Tells widget painter to update screen
        self.widget_parent.update()

    @overrides
    def setAnchorPoints(self):
        """
        Sets the anchor points for the object. Called when object is created, and when scale changes
        Overridden to only have two anchor points
        """
        coil_height = 10 # im sorry
        if self.is_vertical:
            sol_mid_point = (self.width - coil_height) / 2
            self.anchor_points[0].updateLocalPosition(QPoint(int(sol_mid_point)+1, 0))
            self.anchor_points[1].updateLocalPosition(QPoint(int(sol_mid_point)+1, self.height))
            self.anchor_points[2].updateLocalPosition(QPoint(int(sol_mid_point)+1, int(self.height/2+1)))
        else:
            sol_mid_point = (self.height-coil_height)/2 + coil_height
            self.anchor_points[0].updateLocalPosition(QPoint(0                 , int(sol_mid_point) ))
            self.anchor_points[1].updateLocalPosition(QPoint(self.width        , int(sol_mid_point) ))
            self.anchor_points[2].updateLocalPosition(QPoint(int(self.width/2+1) , int(sol_mid_point)))

    def toggle(self):
        """
        Toggle the state of the solenoid
        """

        if self.state == 0:
            self.setState(1, self.voltage, self.current)
        elif self.state == 1:
            self.setState(0, self.voltage, self.current)
        else:
            print("WARNING STATE OF SOLENOID " + str(self._id) + " IS NOT PROPERLY DEFINED")

    def setState(self, state: bool, voltage: float, current: float):
        """
        Set the state of the solenoid
        """

        self.state = state
        self.voltage = voltage
        self.current = current
        self.updateToolTip()

    def updateToolTip(self):
        """
        Called to update the tooltip of the solenoid
        """

        text = ""

        if self.avionics_board != "Undefined" and self.channel != "Undefined":
            text += "Channel: %s\n" % (self.central_widget.window.interface.getPrefix(self.avionics_board) + str(self.channel))
        else:
            text += "Channel:\n"

        if self.state == 1:
            text += "State: Energized\n"
        else:
            text += "State: De-energized\n"

        text += "Voltage: %s V\nCurrent: %s A\n" % (self.voltage, self.current)

        if self.normally_open:
            text += "Normally Open"
        else:
            text += "Normally Closed"

        self.setToolTip_(text)

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
            "normally open": self.normally_open
        }

        # Update the super_dict under the solenoid entry with the solenoid specific data
        super_dict[self.object_name + " " + str(self._id)].update(save_dict)

        return super_dict

    @pyqtSlot(object)
    def updateFromDataPacket(self, data_packet: dict):

        if self.avionics_board != "Undefined" and self.channel != "Undefined":
            board_prefix = self.gui.controlsWindow.interface.getPrefix(self.avionics_board)
            channel_name = board_prefix + "vlv" + str(self.channel)
            state = data_packet[channel_name + ".en"]
            voltage = data_packet[channel_name + ".e"]
            current = data_packet[channel_name + ".i"]
            self.setState(state, voltage, current)

