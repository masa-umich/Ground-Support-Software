from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants


class Tube:

    object_name = "Tube"

    def __init__(self, parent: QWidget,points: [QPoint], fluid: int):
        self.parent = parent
        self.points = points
        self.fluid = fluid
        self.is_being_drawn = False

    def completeTube(self):
        del self.points[-1]
        self.is_being_drawn = False
        for obj in self.parent.object_list:
            obj.setMouseEventTransparency(False)
        self.parent.update()

    def setCurrentPos(self, current_pos: QPoint):
        self.points.append(current_pos)

    def updateCurrentPos(self, current_pos: QPoint):

        for obj in self.parent.object_list:
            obj.setMouseEventTransparency(True)


        diff = self.points[-2] - current_pos

        # If this is the first point allow the user to make a straight line in the x or y direction
        if len(self.points) <= 2:
            if abs(diff.x()) > abs(diff.y()):
                self.points[-1] = QPoint(current_pos.x(), self.points[-2].y())
            else:
                self.points[-1] = QPoint(self.points[-2].x(), current_pos.y())
        # If this is not the first line make sure the new segment is perpendicular to the last segment
        else:
            if abs(self.points[-2].x() - self.points[-3].x()) == 0:
                self.points[-1] = QPoint(current_pos.x(), self.points[-2].y())
            elif abs(self.points[-2].y() - self.points[-3].y()) == 0:
                self.points[-1] = QPoint(self.points[-2].x(), current_pos.y())


    def draw(self):
        self.parent.painter.setPen(Constants.fluidColor[self.fluid])

        path = QPainterPath()

        path.moveTo(self.points[0])

        for point in self.points:
            path.lineTo(point)

        self.parent.painter.drawPath(path)