from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from overrides import overrides


class AnchorPoint(QPushButton):
    """
    QPoint class that holds specific info to anchor points
    """

    def __init__(self, local_pos: QPoint, object_, x_aligned: bool = False, y_aligned: bool = False, parent=None):
        """
        Init for the AnchorPoint

        :param local_pos: local position of the point. Local means relative to the top left corner of the object
        :param object_: object point is assigned to
        :param x_aligned: is the x position of the point aligned with another objects anchor point
        :param y_aligned: is the y position of the point aligned with another objects anchor point
        :param parent: parent window
        """
        # Init the point
        super().__init__(parent)

        self.local_pos = local_pos
        self.object_ = object_
        self.x_aligned = x_aligned
        self.y_aligned = y_aligned
        self.parent = parent
        self.is_drag = False
        self.drag_now_pos = None

        self.setStyleSheet("background-color:transparent;border:0;")
        self.resize(6,6)
        self.show()

        self.updatePosition()

        self.raise_()

    def updatePosition(self):
        """
        Updates the absolute position on the anchor point. Called when object moves
        """
        self.move(self.local_pos.x() + self.object_.position.x() - (self.width()/2), self.local_pos.y() + self.object_.position.y()-(self.height()/2))

    def updateLocalPosition(self, pos: QPoint):
        """
        Updates the local position on the anchor point. Called when scale changesg
        """
        self.local_pos = pos

        self.updatePosition()

    @overrides
    def mousePressEvent(self, event: QMouseEvent):
        """
        Called when mouse is pressed on a button. Used for drag and drop of objects

        :param event: variable holding event data
        """
        # If left click and the button is currently being edited
        if event.button() == Qt.LeftButton & self.object_.is_being_edited:
            # Set drag start position
            self.drag_start_pos = QPoint(3,3)
            self.is_drag = True

        super().mousePressEvent(event)

    @overrides
    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Called when mouse is moving a button. Used for drag and drop of objects

        :param event: variable holding event data
        """
        if event.button() == Qt.LeftButton & self.object_.is_being_edited:
            self.drag_now_pos = event.pos()

        self.object_.widget_parent.update()

        super().mouseMoveEvent(event)

    @overrides
    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)

        #self.is_drag = False
        #self.drag_now_pos = None