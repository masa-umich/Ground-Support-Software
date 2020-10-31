from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from overrides import overrides

from constants import Constants
from MathHelper import MathHelper
from object import BaseObject


"""
Class to handle all tank objects and their functionality 
"""
# TODO: Tanks need to be more similar to solenoids so the base object can be expanded
class Tank(BaseObject):

    object_name = "Tank"

    def __init__(self, widget_parent: QWidget, position: QPointF, fluid: int, width: float = 88*1,
                 height: float = 170*1, name: str = "Tank",
                 scale: float = 1, serial_number: str = '',
                 long_name: str = 'Tank', is_vertical: bool = True,
                 locked: bool = False, position_locked: bool = False, _id: int = None,
                 serial_number_label_pos: str = "Bottom", serial_number_label_local_pos: QPoint = QPoint(0, 0),
                 serial_number_label_font_size: float = 10, long_name_label_pos: str = "Top",
                 long_name_label_local_pos: QPoint = QPoint(0,0), long_name_label_font_size: float = 23,
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

        # TODO: Grab height and width from csv file
        # TODO: Grab object scale from widget_parent

        # Tracks the percentage of fluid in the tank
        self.fillPercent = 0

    @overrides
    def onClick(self):
        """
        When a tank is clicked this function is called
        This is really only useful for adding plots and
        selecting the tank for editing
        """
        super().onClick()

        if not self.widget_parent.parent.is_editing:
            # This is for testing and will normally be used with capacitive level sensor
            self.fillPercent += .05

        # Tells widget painter to update screen
        self.widget_parent.update()

    @overrides
    def draw(self):
        """
        Draws the tank icon on screen
        """
        # Height of curved arc at top and bottom of tank
        arcHeight = 20 * self.scale * self.widget_parent.gui.pixel_scale_ratio[0]

        # Draws the tank outline
        path = QPainterPath()
        if self.is_vertical == True:
            path.moveTo(0,arcHeight)
            path.arcTo(QRectF(0, 0, self.width, arcHeight * 2), 180, -180)
            path.lineTo(self.width, self.height - 2 * arcHeight) 
            path.arcTo(QRectF(self.width, path.currentPosition().y(), - self.width, arcHeight * 2), 180, 180)
            path.lineTo(0, arcHeight)
        
        elif self.is_vertical == False:
            path.moveTo(arcHeight,0)
            path.arcTo(QRectF(0, 0,  arcHeight * 2, self.height), 90, 180) 
            path.lineTo(self.width - arcHeight, self.height) 
            path.arcTo(path.currentPosition().x()-arcHeight,0,arcHeight*2,self.height, -90, 180)
            path.lineTo(arcHeight, 0)
            
        path.translate(self.position.x(), self.position.y()) # Translate it into position
        self.widget_parent.painter.drawPath(path) # Draw Path

        # Debug randomness
        #self.widget_parent.painter.fillRect(QRectF(self.position.x(), self.position.y(), 10, 10), Constants.fluidColor[self.fluid])

        # End tank outline draw

        # TODO: Make this a bit more basic to understand / helper function for filling an arc
        # Fill in bottom arc
        path = QPainterPath()
        self.widget_parent.painter.setPen(Constants.fluidColor[self.fluid])
        self.widget_parent.painter.setBrush(Constants.fluidColor[self.fluid])

        # Maps the fill percentage of the tank to an angle to fill the bottom arc
        bottomArcFillAngle = MathHelper.mapValue(self.fillPercent, 0, arcHeight / self.height, 0, 90)

        path.moveTo(self.position.x() + self.width / 2, self.position.y() + self.height)
        path.arcTo(QRectF(self.position.x(), self.position.y() + self.height - 2 * arcHeight, self.width, arcHeight * 2), 270, bottomArcFillAngle)
        path.lineTo(self.position.x() + self.width / 2, path.currentPosition().y())
        path.lineTo(self.position.x() + self.width / 2, self.position.y() + self.height)

        path.moveTo(self.position.x() + self.width / 2, self.position.y() + self.height)
        path.arcTo(QRectF(self.position.x(), self.position.y() + self.height - 2 * arcHeight, self.width, 2 * arcHeight), 270,
                   -bottomArcFillAngle)
        path.lineTo(self.position.x() + self.width / 2, path.currentPosition().y())
        path.lineTo(self.position.x() + self.width / 2, self.position.y() + self.height)

        self.widget_parent.painter.drawPath(path)
        # End fill in bottom arc

        # Fill in tank body
        # Maps fill percentage to the height of the body to fill
        bodyFillHeight = MathHelper.mapValue(self.fillPercent, arcHeight / self.height, 1 - arcHeight / self.height, 0,
                                       self.height - 2 * arcHeight)

        self.widget_parent.painter.fillRect(QRectF(self.position.x(), self.position.y() - arcHeight + self.height - bodyFillHeight, self.width, bodyFillHeight), Constants.fluidColor[self.fluid])
        # End fill in tank body

        # Fill in top arc
        path = QPainterPath()
        self.widget_parent.painter.setPen(Constants.fluidColor[self.fluid])
        self.widget_parent.painter.setBrush(Constants.fluidColor[self.fluid])

        topArcFillAngle = MathHelper.mapValue(self.fillPercent, 1 - (arcHeight / self.height), 1, 0, 90)

        path.moveTo(self.position.x() + self.width, self.position.y() + arcHeight)
        path.arcTo(QRectF(self.position.x(), self.position.y(), self.width, arcHeight * 2), 0, topArcFillAngle)
        if topArcFillAngle > 0:
            path.lineTo(self.position.x() + self.width / 2, path.currentPosition().y())
            path.lineTo(self.position.x() + self.width / 2, self.position.y() + arcHeight)

        path.moveTo(self.position.x(), self.position.y() + arcHeight)
        path.arcTo(QRectF(self.position.x(), self.position.y(), self.width, arcHeight * 2), 180, -topArcFillAngle)
        if topArcFillAngle > 0:
            path.lineTo(self.position.x() + self.width / 2, path.currentPosition().y())
            path.lineTo(self.position.x() + self.width / 2, self.position.y() + arcHeight)

        self.widget_parent.painter.drawPath(path)

        # self.widget_parent.painter.eraseRect(
        #     QRect(self.long_name_label.pos().x(), self.long_name_label.pos().y(), self.long_name_label.width(),
        #           self.long_name_label.height()))

        self.widget_parent.painter.setBrush(0)
        # End fill in top arc

        super().draw()
