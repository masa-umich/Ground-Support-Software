from PyQt5.QtGui import *

from overrides import overrides

from constants import Constants
from object import BaseObject


class Solenoid(BaseObject):
    """
    Class to handle all solenoid objects and their functionality
    """

    object_name = "Solenoid"

    def __init__(self, widget_parent, position, fluid, isVertical):

        """
        Init the solenoid object
        :param widget_parent: widget this object will be added to
        :param position: position of icon on screen
        :param fluid: fluid in object
        :param isVertical: tracker if object is drawn vertically
        :return:
        """

        # TODO: Still bleah, should have a way to rotate or something
        if isVertical:
            super().__init__(parent=widget_parent, position=position, fluid=fluid, width=18 * 1.75, height=40 * 1.75,name="Solenoid", is_vertical=isVertical, is_being_edited=False)
        else:
            # Initialize base classes
            super().__init__(parent=widget_parent, position=position, fluid=fluid, width= 40*1.75, height = 18*1.75, name = "Solenoid", is_vertical=isVertical, is_being_edited = False)

        # TODO: Grab height and width from csv file
        # TODO: Grab object scale from widget_parent

        # State tracks whether the solenoid is open or closed
        self.state = 0

    @overrides
    def draw(self):
        """
        Draws the solenoid icon on screen
        """

        # Holds the path of lines to draw
        path = QPainterPath()

        # If solenoid is open color it in
        if self.state == 1:
            self.widget_parent.painter.setBrush(Constants.fluidColor[self.fluid])  # This function colors in a path

        # Move path to starting position
        path.moveTo(0, 0)  # Top left corner

        # = 0 -> Draw horizontally
        if self.is_vertical == 0:
            path.lineTo(0,self.height)  # Straight Down
            path.lineTo(self.width,0)  # Diag to upper right
            path.lineTo(self.width, self.height)  # Straight Up
            path.lineTo(0, 0)

            # TODO: Implement three way Solenoid
            # path.moveTo(self.width/2, self.height/2)
            # path.lineTo((self.width/2) - (self.height/2), (self.height/2) - (self.width /2))
            # path.lineTo((self.width/2) + (self.height/2), (self.height/2) - (self.width /2))
            # path.lineTo(self.width/2, self.height/2)
        else:  # Draw vertically
            path.lineTo(self.width, 0)
            path.lineTo(0, self.height)
            path.lineTo(self.width, self.height)
            path.lineTo(0, 0)


        path.translate(self.position.x(), self.position.y())

        self.widget_parent.painter.drawPath(path)

        self.widget_parent.painter.setBrush(0)

        super().draw()

        # This is debug, draws a box around the origin of object
        #self.widget_parent.painter.fillRect(QRectF(self.position.x(), self.position.y(), 7, 7),Constants.fluidColor[self.fluid])

    @overrides
    def onClick(self):
        """
        When a solenoid is clicked this function is called
        """

        super().onClick()

        if not self.widget_parent.window.is_editing:
            # Toggle state of solenoid
            self.toggle()

        # Tells widget painter to update screen
        self.widget_parent.update()

    def toggle(self):
        """
        Toggle the state of the solenoid
        """

        if self.state == 0:
            self.state = 1
            self.setToolTip_("State: Open")
        elif self.state == 1:
            self.state = 0
            self.setToolTip_("State: Closed")
        else:
            print("WARNING STATE OF SOLENOID " + str(self._id) + " IS NOT PROPERLY DEFINED")
