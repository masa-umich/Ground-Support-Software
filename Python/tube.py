from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants


class Tube:

    object_name = "Tube"

    def __init__(self, parent: QWidget,points: [QPoint], fluid: int, tube_id: int = None):
        self.parent = parent
        self.widget_parent = parent
        self.points = points

        if tube_id is not None:
            self.tube_id = tube_id
            self.widget_parent.last_tube_id = max(self.widget_parent.last_tube_id, self.tube_id)
        else:
            self.tube_id = self.widget_parent.last_tube_id + 1
            self.widget_parent.last_tube_id = self.tube_id

        self.fluid = fluid
        self.is_being_drawn = False
        self.draw_direction = "None"  # Either "Horizontal" or "Vertical"

    def completeTube(self):
        del self.points[-1]
        self.is_being_drawn = False
        for obj in self.widget_parent.object_list:
            obj.setMouseEventTransparency(False)
            for obj_ap in obj.anchor_points:
                obj_ap.x_aligned = False
                obj_ap.y_aligned = False

        self.widget_parent.is_drawing = False
        self.widget_parent.update()

    def setCurrentPos(self, current_pos: QPoint):
        self.points.append(current_pos)

    def updateCurrentPos(self, current_pos: QPoint):

        for obj in self.widget_parent.object_list:
            obj.setMouseEventTransparency(True)

        diff = self.points[-2] - current_pos

        # If this is the first point allow the user to make a straight line in the x or y direction
        if len(self.points) <= 2:
            if abs(diff.x()) > abs(diff.y()):
                self.points[-1] = QPoint(current_pos.x(), self.points[-2].y())
                self.draw_direction = "Horizontal"
            else:
                self.points[-1] = QPoint(self.points[-2].x(), current_pos.y())
                self.draw_direction = "Vertical"
        # If this is not the first line make sure the new segment is perpendicular to the last segment
        else:
            if abs(self.points[-2].x() - self.points[-3].x()) == 0:
                self.points[-1] = QPoint(current_pos.x(), self.points[-2].y())
                self.draw_direction = "Horizontal"
            elif abs(self.points[-2].y() - self.points[-3].y()) == 0:
                self.points[-1] = QPoint(self.points[-2].x(), current_pos.y())
                self.draw_direction = "Vertical"

        # This will check for tube end alignment with object anchor points
        for obj in self.widget_parent.object_list:
            for obj_ap in obj.anchor_points:
                obj_ap.x_aligned = False
                obj_ap.y_aligned = False
                if obj_ap.x()-5 < self.points[-1].x() < obj_ap.x()+5 and self.draw_direction == "Horizontal":
                    self.points[-1] = QPoint(obj_ap.x() + 3, self.points[-1].y())
                    obj_ap.x_aligned = True
                if obj_ap.y()-5 < self.points[-1].y() < obj_ap.y()+5  and self.draw_direction == "Vertical":
                    self.points[-1] = QPoint(self.points[-1].x(),obj_ap.y() + 3)
                    obj_ap.y_aligned = True

        self.widget_parent.update()

    def draw(self):
        # Default pen qualities
        pen = QPen()
        pen.setWidth(Constants.line_width/2)
        pen.setColor(Constants.fluidColor[self.fluid])
        self.widget_parent.painter.setPen(pen)

        path = QPainterPath()

        path.moveTo(self.points[0])

        for point in self.points:
            path.lineTo(point)

        self.widget_parent.painter.drawPath(path)

    def generateSaveDict(self):
        """
        Here is where an tube data is moved into a dict, it will be combined with all the other tubes data and
        saved to a json file. Unfortuantely for any data to be saved it must be manually inserted here and also manually
        pulled from the load function. It has the benefit of being easily readable though
        """

        # Put all the points in their own dictionary
        points_dict = {}
        i = 0
        for point in self.points:
            points_dict[i] = {"x": point.x()/self.parent.gui.pixel_scale_ratio[0], "y": point.y()/self.parent.gui.pixel_scale_ratio[1]}
            i = i + 1

        # Put it all together
        save_dict = {
            self.object_name + " " + str(self.tube_id): {
                "tube id": self.tube_id,
                "fluid": self.fluid,
                "bend positions": points_dict
            }
        }

        return save_dict