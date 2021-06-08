from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants
from overrides import overrides

import math


class Tube:

    object_name = "Tube"

    def __init__(self, parent: QWidget, points: [QPoint], fluid: int, attachment_aps, tube_id: int = None, line_width: int = Constants.line_width/2):
        self.parent = parent
        self.widget_parent = parent
        self.points = points
        self.attachment_aps = attachment_aps
        self.tube_anchor_points = []
        self.line_width = line_width

        if tube_id is not None:
            self.tube_id = tube_id
            self.widget_parent.last_tube_id = max(self.widget_parent.last_tube_id, self.tube_id)
            for i in range(1,len(self.points)-1):
                self.tube_anchor_points.append(TubeAnchorPoint(self.widget_parent, self,self.points[i], i))

        else:
            self.tube_id = self.widget_parent.last_tube_id + 1
            self.widget_parent.last_tube_id = self.tube_id

        self.fluid = fluid
        self.is_being_drawn = False
        self.draw_direction = "None"  # Either "Horizontal" or "Vertical"

    def completeTube(self, deleteLast: bool = True):
        if deleteLast:
            del self.points[-1]
        self.is_being_drawn = False
        self.widget_parent.setObjectsMouseTransparency(False)
        self.widget_parent.resetObjectsAnchorPointAlignment()

        self.widget_parent.is_drawing = False
        self.widget_parent.update()

        self.widget_parent.window.statusBar().showMessage("Tube completed")

    def deleteTube(self):
        for ap in self.attachment_aps:
            ap.tube = None
        for tube_ap in self.tube_anchor_points:
            tube_ap.deleteLater()
            del tube_ap

        self.widget_parent.tube_list.remove(self)
        self.widget_parent.is_drawing = False
        self.widget_parent.should_ignore_mouse_release = False
        self.widget_parent.setObjectsMouseTransparency(False)
        del self

    def setCurrentPos(self, current_pos: QPoint, deleteLast: bool = False):
        if deleteLast:
            del self.points[-1]

        self.points.append(current_pos)
        if len(self.points) < 2:
            self.points.append(current_pos)

        if len(self.points) > 2:
            self.tube_anchor_points.append(TubeAnchorPoint(self.widget_parent, self, self.points[-2], len(self.points)-2))

    def updateCurrentPos(self, current_pos: QPoint):

        if len(self.points) < 2:
            return

        self.widget_parent.setObjectsMouseTransparency(True)

        diff = self.points[-2] - current_pos

        # If this is the first point allow the user to make a straight line in the x or y direction
        if len(self.points) <= 2:
            if abs(diff.x()) > abs(diff.y()):
                self.points[-1] = QPoint(current_pos.x(), self.points[-2].y())
                self.draw_direction = "Horizontal"
            else:
                self.points[-1] = QPoint(self.points[-2].x(), current_pos.y())
                self.draw_direction = "Vertical"
        # If this is not the first line make sure the new segment is perpendicular to the last segment, if shift is
        # being held down, then the new segment is parallel
        else:
            mod = QApplication.keyboardModifiers()
            # If the two last x points are in line, the previous line was vertical, if shift is being held continue
            # vertical, otherwise make it horizontal
            if abs(self.points[-2].x() - self.points[-3].x()) == 0:
                if mod == Qt.ShiftModifier:
                    self.points[-1] = QPoint(self.points[-2].x(), current_pos.y())
                    self.draw_direction = "Vertical"
                else:
                    self.points[-1] = QPoint(current_pos.x(), self.points[-2].y())
                    self.draw_direction = "Horizontal"
            # If the two last y points are in line, the previous line was horizontal, if shift is being held continue
            # horizontal, otherwise make it vertical
            elif abs(self.points[-2].y() - self.points[-3].y()) == 0:
                if mod == Qt.ShiftModifier:
                    self.points[-1] = QPoint(current_pos.x(), self.points[-2].y())
                    self.draw_direction = "Horizontal"
                else:
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

        # This will check for tube end alignment with tube anchor points
        for tube in self.widget_parent.tube_list:
            if tube is not self:
                for tube_ap in tube.tube_anchor_points:
                    tube_ap.x_aligned = False
                    tube_ap.y_aligned = False
                    if tube_ap.x()-5 < self.points[-1].x() < tube_ap.x()+5 and self.draw_direction == "Horizontal":
                        self.points[-1] = QPoint(tube_ap.x() + 3, self.points[-1].y())
                        tube_ap.x_aligned = True
                    if tube_ap.y()-5 < self.points[-1].y() < tube_ap.y()+5  and self.draw_direction == "Vertical":
                        self.points[-1] = QPoint(self.points[-1].x(),tube_ap.y() + 3)
                        tube_ap.y_aligned = True

        self.widget_parent.update()

    def draw(self):
        # Default pen qualities
        pen = QPen()
        pen.setWidth(self.line_width)
        pen.setColor(Constants.fluidColor[self.fluid])
        self.widget_parent.painter.setPen(pen)

        path = QPainterPath()

        if len(self.points) > 0:
            path.moveTo(self.points[0])
            for point in self.points:
                path.lineTo(point)

            self.widget_parent.painter.drawPath(path)

        if self.widget_parent.centralWidget.is_editing:
            for tube_ap in self.tube_anchor_points:
                tube_ap.show()
                self.widget_parent.painter.setPen(pen)
                tube_ap.draw()
        else:
            self.hideTubeAnchorPoints()

    def hideTubeAnchorPoints(self):
        for tube_ap in self.tube_anchor_points:
            tube_ap.hide()

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
        # TODO: Add attachment save id
        save_dict = {
            self.object_name + " " + str(self.tube_id): {
                "tube id": self.tube_id,
                "fluid": self.fluid,
                "bend positions": points_dict,
                "line width": self.line_width
            }
        }

        return save_dict


# TODO: Make a Anchor Point class that Tube and Objects can both subclass from and share functionality
class TubeAnchorPoint(QPushButton):
    """
    Very similar to the anchor point class, reduce/ specific functionality for drawing tube lines
    """

    def __init__(self, parent, tube, point, points_index):
        # Init the point
        super().__init__(parent)
        self.controlsWidget = parent
        self.tube = tube
        self.gui = self.controlsWidget.gui
        self.points_index = points_index
        self.x_aligned = False
        self.y_aligned = False
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.context_menu = QMenu(self.controlsWidget)
        self.context_menu.addAction("Delete Tube")
        self.context_menu.addAction("Change Fluid")
        self.context_menu.addAction("Increase Line Width")
        self.context_menu.addAction("Decrease Line Width")
        self.customContextMenuRequested.connect(lambda *args: self.contextMenuEvent_(*args))

        self.setStyleSheet("background-color:transparent;border:0;")

        # Below makes sure the anchor point size is rounded to the nearest odd number
        self.resize(2 * math.floor((6 * self.gui.pixel_scale_ratio[0]) / 2),
                    2 * math.floor((6 * self.gui.pixel_scale_ratio[0]) / 2))

        self.move(QPoint(point.x() - self.size().width()/2, point.y() - self.size().height()/2))

        self.show()

        self.controlsWidget.window.statusBar().showMessage("Tube point created at " + "(" + str(self.x()) + ", " + str(self.y()) + ")")


    def draw(self):
        """
        Draws the anchor point on the screen, also draws the alignment lines
        """
        # Draws the box
        self.controlsWidget.painter.drawRect(QRectF(self.x(), self.y(), self.width(), self.height()))
        self.controlsWidget.painter.eraseRect(QRectF(self.x(), self.y(), self.width(), self.height()))

        # Draws the yellow dashed alignment lines when dragging the ap's object or drawing the ap's tube
        if self.controlsWidget.is_drawing:
            pen = QPen()
            pen.setColor(Qt.yellow)
            pen.setStyle(Qt.DashLine)
            if self.gui.platform == "Windows":
                pen.setWidth(2)
            elif self.gui.platform == "OSX":
                pen.setWidth(1)
            self.controlsWidget.painter.setPen(pen)

            if self.x_aligned:
                self.controlsWidget.painter.drawLine(QPoint(self.x() + (5 * self.gui.pixel_scale_ratio[0]), 0),
                                             QPoint(self.x(), self.gui.screenResolution[1]))
            if self.y_aligned:
                self.controlsWidget.painter.drawLine(QPoint(0, self.y() + (6 * self.gui.pixel_scale_ratio[1])),
                                             QPoint(self.gui.screenResolution[0], self.y()))

    def contextMenuEvent_(self, event):
        """
        Handler for context menu.
        :param event: default event from pyqt
        :return: action: passes the action to potential overridden methods to handle non default cases
        """

        action = self.context_menu.exec_(self.mapToGlobal(event))

        # The actions that go in here can be found in the _initContextMenu function in this class
        if action is not None:
            if action.text() == "Delete Tube":
                self.tube.deleteTube()
                self.controlsWidget.window.statusBar().showMessage("Tube deleted")
            elif action.text() == "Change Fluid":
                # TODO: Don't cycle through tubes like this it sucks
                max_ = len(Constants.fluid) / 2 - 1
                if self.tube.fluid < max_:
                    self.tube.fluid = self.tube.fluid + 1
                else:
                    self.tube.fluid = 0
                self.controlsWidget.window.statusBar().showMessage("Tube fluid set to " + Constants.fluid[self.tube.fluid])
            elif action.text() == "Increase Line Width":
                self.tube.line_width = self.tube.line_width + 1
                self.controlsWidget.window.statusBar().showMessage("Tube width increased to " + str(self.tube.line_width))
            elif action.text() == "Decrease Line Width":
                self.tube.line_width = self.tube.line_width - 1
                if self.tube.line_width < 1:
                    self.tube.line_width = 1
                self.controlsWidget.window.statusBar().showMessage("Tube width decreaseed to " + str(self.tube.line_width))

    @overrides
    def mousePressEvent(self, event: QMouseEvent):
        """
        Called when mouse is pressed on a anchor point. Used for drawing lines between objects

        :param event: variable holding event data
        """

        # If left click and the button is currently being edited
        # TODO: Implement multiple tube runs on one line
        # if event.button() == Qt.LeftButton and self.widget.is_drawing is False:
        #     # Set drag start position
        #     if self.tube is not None:
        #         self.tube.deleteTube()
        #
        #     self.tube = Tube(self.widget, [self.pos() + QPoint(self.width() / 2, self.height() / 2),
        #                                    self.pos() + QPoint(self.width() / 2, self.height() / 2)],
        #                      self.object_.fluid, [self])
        #     self.tube.is_being_drawn = True
        #     self.widget.is_drawing = True
        #     self.widget.setMouseTracking(True)
        #     self.widget.tube_list.append(self.tube)

        if event.button() == Qt.LeftButton and self.controlsWidget.is_drawing is True:
            self.controlsWidget.is_drawing = False
            for tube in self.controlsWidget.tube_list:
                if tube.is_being_drawn:
                    if tube.draw_direction == "Vertical":
                        tube.setCurrentPos(QPoint(tube.points[-1].x(),self.tube.points[self.points_index].y()), True)
                        tube.setCurrentPos(self.tube.points[self.points_index])
                    else:
                        tube.setCurrentPos(QPoint(self.tube.points[self.points_index].x(),tube.points[-1].y()), True)
                        tube.setCurrentPos(self.tube.points[self.points_index])

                    tube.completeTube(False)

        elif event.button() == Qt.LeftButton and self.controlsWidget.is_drawing is False:
            self.tube.is_being_drawn = True
            self.controlsWidget.is_drawing = True
            self.controlsWidget.setMouseTracking(True)
            del self.tube.points[self.points_index+2:]  # Need to keep two extra points for drawing sake, idrk why
            del self.tube.tube_anchor_points[self.points_index:]
            if len(self.tube.attachment_aps) > 1:
                if len(self.tube.attachment_aps) > 2:
                    print("WEIRD SHIT IN TUBE MOUSE PRESS PLEASE LOOK AT")
                del self.tube.attachment_aps[-1]

        #super().mousePressEvent(event)