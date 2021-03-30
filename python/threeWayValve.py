from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from overrides import overrides
from datetime import datetime

from constants import Constants
from object import BaseObject


class ThreeWayValve(BaseObject):
    """
    Class to handle all ThreeWayValve objects and their functionality
    """

    object_name = "3 Way Valve"

    def __init__(self, widget_parent: QWidget, position: QPointF, fluid: int, width: float = 40 *1,
                 height: float = 27*1, name: str = "3 Way Valve",
                 scale: float = 1, serial_number: str = '',
                 long_name: str = '3 Way Valve', is_vertical: bool = False,
                 locked: bool = False, position_locked: bool = False, _id: int = None,
                 serial_number_label_pos: str = "Bottom", serial_number_label_local_pos: QPoint = QPoint(0,0),
                 serial_number_label_font_size: float = 10, long_name_label_pos: str = "Top",
                 long_name_label_local_pos: QPoint = QPoint(0,0), long_name_label_font_size: float = 12,
                 long_name_label_rows: int = 1, channel: str = 'Undefined', board: str = 'Undefined'):

        """
        Initializer for ThreeWayValve

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


        # TODO: Grab height and width from csv file
        # TODO: Grab object scale from widget_parent

        # State tracks whether the ThreeWayValve is open or closed
        self.state = 0
        self.voltage = 0
        self.current = 0
        self.sec_width = 18*self.widget_parent.gui.pixel_scale_ratio[0] #width of a valve "section" same as 2 way valve width
        self.setAnchorPoints()
        self.channel = channel
        self.avionics_board = board
        self.client = self.widget_parent.window.client_dialog.client

        self.updateToolTip()
        
    @overrides
    def draw(self):
        """
        Draws the ThreeWayValve icon on screen
        """
        # Holds the path of lines to draw
        path = QPainterPath()
        
        #Sets the two brush types for each valve path based on whether the valve is energized or not
        if self.state == 1:
            fill = [QBrush(Constants.fluidColor[self.fluid],Qt.SolidPattern),QBrush(Constants.fluidColor[self.fluid],Qt.SolidPattern), QBrush(0)]
        else:
            fill = [QBrush(0),QBrush(Constants.fluidColor[self.fluid],Qt.Dense5Pattern),QBrush(Constants.fluidColor[self.fluid],Qt.Dense5Pattern)]

        # Move path to starting position
        path.moveTo(0, 0)  # Top left corner

        
        if self.is_vertical == 0: # Draw horizontally
            # Draw port 1
            self.widget_parent.painter.setBrush(fill[0])
            path.lineTo(0,self.sec_width) 
            path.lineTo(self.width/2,self.sec_width/2)
            path.lineTo(0, 0)
            path.translate(self.position.x(), self.position.y())
            self.widget_parent.painter.drawPath(path)               
            
            # Draw port 2
            path = QPainterPath()
            self.widget_parent.painter.setBrush(fill[1])
            path.moveTo(self.width/2,self.sec_width/2)
            path.lineTo((self.width-self.sec_width)/2,self.height)
            path.lineTo((self.width+self.sec_width)/2,self.height)
            path.lineTo(self.width/2,self.sec_width/2)
            path.translate(self.position.x(), self.position.y())
            self.widget_parent.painter.drawPath(path)
            
            # Draw port 3
            path = QPainterPath()
            self.widget_parent.painter.setBrush(fill[2])
            path.moveTo(self.width/2,self.sec_width/2) 
            path.lineTo(self.width,0)
            path.lineTo(self.width, self.sec_width)
            path.lineTo(self.width/2,self.sec_width/2)
            path.translate(self.position.x(), self.position.y())
            self.widget_parent.painter.drawPath(path)

        else:  # Draw vertically
            # Draw port 1
            self.widget_parent.painter.setBrush(fill[0])
            path.lineTo(self.sec_width, 0)
            path.lineTo(self.sec_width/2, self.height/2)
            path.lineTo(0, 0)
            path.translate(self.position.x(), self.position.y())
            self.widget_parent.painter.drawPath(path)    
            
            # Draw port 2
            path = QPainterPath()
            self.widget_parent.painter.setBrush(fill[1])
            path.moveTo(self.sec_width/2,self.height/2)
            path.lineTo(self.width,(self.height-self.sec_width)/2)
            path.lineTo(self.width,(self.height+self.sec_width)/2)
            path.lineTo(self.sec_width/2,self.height/2)
            path.translate(self.position.x(), self.position.y())
            self.widget_parent.painter.drawPath(path) 
            
            # Draw port 3
            path = QPainterPath()
            self.widget_parent.painter.setBrush(fill[2])
            path.moveTo(self.sec_width/2,self.height/2) 
            path.lineTo(0, self.height)
            path.lineTo(self.sec_width, self.height)
            path.lineTo(self.sec_width/2,self.height/2)
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
            self.anchor_points[0].updateLocalPosition(QPoint(0,int(self.sec_width/2)))
            self.anchor_points[1].updateLocalPosition(QPoint(self.width ,int(self.sec_width/2)))
            self.anchor_points[2].updateLocalPosition(QPoint(self.width/2,0))
            self.anchor_points[3].updateLocalPosition(QPoint(self.width/2, self.height))
        else:
            self.anchor_points[0].updateLocalPosition(QPoint(int(self.sec_width/2),0))
            self.anchor_points[1].updateLocalPosition(QPoint(int(self.sec_width/2),self.height))
            self.anchor_points[2].updateLocalPosition(QPoint(0,int(self.height/2)))
            self.anchor_points[3].updateLocalPosition(QPoint(self.width, int(self.height/2)))
        
    def onClick(self):
        """
        When a ThreeWayValve is clicked this function is called
        """

        super().onClick()

        if not self.widget_parent.parent.is_editing:
    
            if self.gui.debug_mode == False:
                # Toggle state of 3-way
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
                    self.client.command(3, cmd_dict)
            else:
                self.toggle()
            

        # Tells widget painter to update screen
        self.widget_parent.update()

    def toggle(self):
        """
        Toggle the state of the ThreeWayValve
        """

        if self.state == 0:
            self.state = 1
            self.setToolTip_("State: Open")
        elif self.state == 1:
            self.state = 0
            self.setToolTip_("State: Closed")
        else:
            print("WARNING STATE OF ThreeWayValve " + str(self._id) + " IS NOT PROPERLY DEFINED")
    
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

        if self.state == 1:
            text += "State: Energized\n"
        else:
            text += "State: De-energized\n"
        
        text += "Voltage: %s V\nCurrent: %s A" % (self.voltage, self.current)
        
        # if self.normally_open:
        #     text += "Normally Open"
        # else:
        #     text += "Normally Closed"

        self.setToolTip_(text)

    # There is currently no ThreeWayValve specific data that needs to be persistent but if some ever does it goes here
    @overrides
    def generateSaveDict(self):
        """
        Generates dict of data to save. Most of the work happens in the object class but whatever ThreeWayValve specific
        info needs to be saved is added here.
        """
    
        # Gets the BaseObject data that needs to be saved
        super_dict = super().generateSaveDict()
    
        # Extra data the ThreeWayValve contains that needs to be saved
        save_dict = {
            "channel": self.channel,
            "board": self.avionics_board,
            # "normally open": self.normally_open
        }
    
        # Update the super_dict under the ThreeWayValve entry with the ThreeWayValve specific data
        super_dict[self.object_name + " " + str(self._id)].update(save_dict)
    
        return super_dict