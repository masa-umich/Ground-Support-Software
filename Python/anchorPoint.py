from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from overrides import overrides
from tube import Tube

import math


class AnchorPoint(QPushButton):
    """
    QPoint class that holds specific info to anchor points
    """

    # TODO: The parent system here seems messed up
    def __init__(self, local_pos: QPoint, object_, local_id: int, x_aligned: bool = False, y_aligned: bool = False, parent=None):
        """
        Init for the AnchorPoint

        :param local_pos: local position of the point. Local means relative to the top left corner of the object
        :param object_: object point is assigned to
        :param x_aligned: is the x position of the point aligned with another objects anchor point
        :param y_aligned: is the y position of the point aligned with another objects anchor point
        :param parent: Controls widget
        :param local_id: the local id of the anchor point, for example if an object has 4, it would be one of 0-3
        """
        # Init the point
        super().__init__(parent)
        self.parent = parent
        self.widget = parent
        self.gui = object_.gui
        self.object_ = object_
        self.local_pos = local_pos
        self.local_id = local_id
        self.x_aligned = x_aligned
        self.y_aligned = y_aligned
        self.tube = None


        self.setStyleSheet("background-color:transparent;border:0;")
        # Below makes sure the anchor point size is rounded to the nearest odd number
        self.resize(2 * math.floor((6 * self.gui.pixel_scale_ratio[0]) / 2), 2 * math.floor((6 * self.gui.pixel_scale_ratio[0]) / 2))
        self.show()

        self.middle = QPoint(int(self.pos().x() + self.size().width()/2), int(self.pos().y() + self.size().height()/2))

        self.updatePosition()

        self.raise_()

    def updatePosition(self):
        """
        Updates the absolute position on the anchor point. Called when object moves
        """
        self.move(int(self.local_pos.x() + self.object_.position.x() - (self.width()/2)), int(self.local_pos.y() + self.object_.position.y()-(self.height()/2)))
        self.middle = QPoint(int(self.pos().x() + self.size().width() / 2), int(self.pos().y() + self.size().height() / 2))

    def updateLocalPosition(self, pos: QPoint):
        """
        Updates the local position on the anchor point. Called when scale changesg
        """
        self.local_pos = pos

        self.updatePosition()

    def draw(self):
        """
        Draws the anchor point on the screen, also draws the alignment lines
        """
        # Draws the box
        self.widget.painter.drawRect(QRectF(self.x(), self.y(), self.width(), self.height()))
        self.widget.painter.eraseRect(QRectF(self.x(), self.y(), self.width(), self.height()))

        # Draws the yellow dashed alignment lines when dragging the ap's object or drawing the ap's tube
        if self.object_.is_being_dragged or self.widget.is_drawing:
            pen = QPen()
            pen.setColor(Qt.yellow)
            pen.setStyle(Qt.DashLine)
            if self.gui.platform == "Windows":
                pen.setWidth(2)
            elif self.gui.platform == "OSX":
                pen.setWidth(1)
            self.widget.painter.setPen(pen)

            if self.x_aligned:
                self.widget.painter.drawLine(QPoint(self.x() + (5 * self.gui.pixel_scale_ratio[0]), 0),
                                                    QPoint(self.x(), self.gui.screenResolution[1]))
            if self.y_aligned:
                self.widget.painter.drawLine(QPoint(0, self.y() + (6 * self.gui.pixel_scale_ratio[1])),
                                                    QPoint(self.gui.screenResolution[0], self.y()))

    @overrides
    def mousePressEvent(self, event: QMouseEvent):
        """
        Called when mouse is pressed on a anchor point. Used for drawing lines between objects

        :param event: variable holding event data
        """
        # If left click and the button is currently being edited
        if event.button() == Qt.LeftButton and self.widget.is_drawing is False:
            # Set drag start position
            if self.tube is not None:
                self.tube.deleteTube()
                
            self.tube = Tube(self.widget, [self.middle, self.middle],self.object_.fluid, [self])
            self.tube.is_being_drawn = True
            self.widget.is_drawing = True
            self.widget.setMouseTracking(True)
            self.widget.tube_list.append(self.tube)
            self.gui.setStatusBarMessage("Tube draw started")

        elif event.button() == Qt.LeftButton:
            self.widget.is_drawing = False
            for tube in self.parent.tube_list:
                if tube.is_being_drawn:
                    if tube.draw_direction == "Vertical":
                        tube.setCurrentPos(QPoint(tube.points[-1].x(), self.middle.y()), True)
                        tube.setCurrentPos(self.middle)
                    else:
                        tube.setCurrentPos(QPoint(self.middle.x(), tube.points[-1].y()), True)
                        tube.setCurrentPos(self.middle)

                    tube.completeTube(False)
                    tube.attachment_aps.append(self)

        super().mousePressEvent(event)

    @overrides
    def deleteLater(self):
        if self.tube is not None:
            self.widget.tube_list.remove(self.tube)
            del self.tube

        super().deleteLater()

    @overrides
    def mouseMoveEvent(self, event: QMouseEvent):
        super().mouseMoveEvent(event)

    @overrides
    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)
