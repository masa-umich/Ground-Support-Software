from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from overrides import overrides
from object import BaseObject

from constants import Constants


class GenSensor(BaseObject):

    object_name = "Generic Sensor"

    def __init__(self, widget_parent: QWidget, position: QPointF, fluid: int, width: float = 55*1,
                 height: float = 20*1, name: str = "PT",
                 scale: float = 1, serial_number: str = '',
                 long_name: str = 'Sensor', is_vertical: bool = False,
                 locked: bool = False, position_locked: bool = False, _id: int = None,
                 serial_number_label_pos: str = "Bottom", serial_number_label_local_pos: QPoint = QPoint(0, 0),
                 serial_number_label_font_size: float = 10, long_name_label_pos: str = "Top",
                 long_name_label_local_pos: QPoint = QPoint(0, 0), long_name_label_font_size: float = 12,
                 long_name_label_rows: int = 1, channel: str = 'Undefined',
                 board: str = 'Undefined', long_name_visible:bool = True, serial_number_visible:bool = True):

        """
        Initializer for genSensor

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

        # Initialize base classes

        super().__init__(parent=widget_parent, position=position, fluid=fluid, width=width, height=height,
                         name=name, is_vertical=is_vertical, scale=scale,
                         serial_number=serial_number, long_name=long_name, locked=locked, position_locked=position_locked,
                         _id=_id, serial_number_label_pos=serial_number_label_pos,
                         serial_number_label_local_pos=serial_number_label_local_pos,
                         serial_number_label_font_size=serial_number_label_font_size,
                         long_name_label_pos=long_name_label_pos, long_name_label_local_pos=long_name_label_local_pos,
                         long_name_label_font_size=long_name_label_font_size,
                         long_name_label_rows=long_name_label_rows,long_name_visible= long_name_visible,
                         serial_number_visible = serial_number_visible)

        self.widget_parent = widget_parent  # Important for drawing icon
        self.gui = self.widget_parent.gui
        self.interface = self.widget_parent.window.interface
        self.units = ""
        self.channel = channel
        self.avionics_board = board
        self.measurement = 0
        self.measurement_label = QLabel(self.widget_parent)
        self.setUnits()
        self._initMeasurementLabel()

        self.updateToolTip()

        #self.measurement_label.setStyleSheet("background-color:" + Constants.MASA_Blue_color.name() + "; border: none")

    def _initMeasurementLabel(self):
        """
        Inits the measurement label
        """
        self.measurement_label.setFixedSize(QSize(self.width, self.height))
        self.measurement_label.move(self.position.x(), self.position.y())
        self.measurement_label.setText(str(self.measurement) + " " + self.units)
        self.measurement_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.measurement_label.setStyleSheet('color: white')

        # Get font and set it
        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily("Arial")
        font.setPointSize(12 * self.gui.font_scale_ratio)
        self.measurement_label.setFont(font)

        self.measurement_label.show()
        self.measurement_label.lower()

    def setMeasurement(self, measurement: float):
        """
        Set measurement of the sensor
        :param measurement: new measurement
        """
        self.measurement = measurement
        self.measurement_label.setText(str(self.measurement)+ " " + self.units)

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
        self.setUnits()
        self.updateToolTip()
    
    def setUnits(self):
        """
        Sets units from config
        """
        unit_dict = self.interface.units
        if self.channel in self.interface.channels:
            units = unit_dict[self.channel]
            if units == 'ul':
                self.units = ''
            else:
                self.units = units
            self.measurement_label.setText(str(self.measurement) + " " + self.units)
            
    @overrides
    def move(self, point: QPoint):
        """
        Move object to a new position
        :param point: point to move to
        """
        super().move(point)

        if self.position_locked == False and self.locked == False:
            self.measurement_label.move(point)

    @overrides
    def onClick(self):
        """
        Called when the Sensor is clicked
        """
        if not self.widget_parent.parent.is_editing:
            if self.gui.debug_mode:
                self.setMeasurement(self.measurement + 50)

        super().onClick()

    @overrides
    def setScale(self, scale):
        """
        Called when the Sensor is clicked
        """
        font = self.measurement_label.font()
        size = font.pointSizeF()
        if scale < self.scale:
            font.setPointSizeF((size-1) * self.gui.font_scale_ratio)
        else:
            font.setPointSizeF((size + 1) * self.gui.font_scale_ratio)

        self.measurement_label.setFont(font)

        super().setScale(scale)

        self.measurement_label.setFixedSize(QSize(self.width, self.height))
        self.measurement_label.move(self.position.x(), self.position.y())
        self.measurement_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)



    @overrides
    def draw(self):
        """
        Draws the Sensor icon on screen
        """
        self.widget_parent.painter.drawRect(QRect(self.position.x(), self.position.y(), self.width, self.height))
        self.widget_parent.painter.setBrush(0)
        
        super().draw()
        
    @overrides
    def deleteSelf(self):
        """
        Delete itself
        """
        self.measurement_label.deleteLater()
        del self.measurement_label

        super().deleteSelf()

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

    def updateToolTip(self):
        """
        Called to update the tooltip of the sensor
        """

        text = ""
        text += self.channel
        self.setToolTip_(text)