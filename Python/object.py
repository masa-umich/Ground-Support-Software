from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants
from plotButton import PlotButton
from customLabel import CustomLabel
from anchorPoint import AnchorPoint


"""
Base class for GUI objects. Used to define parameters all GUI objects need
"""


class BaseObject:

    object_name = "Default Object"

    """----------------------------------------------------------------------------------------------------------------
    INIT SECTION 
    ----------------------------------------------------------------------------------------------------------------"""


    def __init__(self, parent: QWidget, position: QPointF, fluid: int, width: float, height: float, name: str,
                 scale: float = 1, avionics_number: int = 5, short_name: str = 'OX-SN-G07', safety_status: int = -1,
                 long_name: str = 'LOX Dewar Drain', is_vertical: bool = False, is_being_edited: bool = False,
                 is_being_dragged: bool = False, locked: bool = False, position_locked: bool = False,
                 long_name_label_position_num: int = 0):
        """
        Initializer for base class

        :param parent: parent widget
        :param position: position of icon on screen
        :param fluid: fluid in object
        :param width: width of object
        :param height: height of object
        :param name: name of object
        :param scale: scale applied to the object
        :param avionics_number: avionics identifier
        :param short_name: abbreviated name on schematics
        :param safety_status: safety criticality
        :param long_name: human-readable name for display on screen
        :param is_vertical: tracker if object is drawn vertically
        :param is_being_edited: tracker if object is drawn vertically
        :param is_being_dragged: tracker if object is currently being dragged by user
        :param locked: tracker if the object is locked from editing
        :param position_locked: tracker if the object position is locked
        :param long_name_label_position_num: num specifying the location of the label -> Move to pos based system
        """
        super().__init__()

        self.widget_parent = parent  # Important for drawing icon
        self.gui = self.widget_parent.gui
        self._id = len(self.widget_parent.object_list)  # Very important! DO NOT CHANGE FROM WHAT PROGRAM SET
        self.position = position
        self.fluid = fluid
        self.width = width * self.widget_parent.gui.pixel_scale_ratio[0]
        self.height = height * self.widget_parent.gui.pixel_scale_ratio[0]
        self.name = name
        self.scale = scale
        self.avionics_number = avionics_number
        self.short_name = short_name
        self.safety_status = safety_status
        self.long_name = long_name
        self.is_vertical = is_vertical
        self.is_being_edited = is_being_edited
        self.is_being_dragged = is_being_dragged
        self.locked = locked
        self.position_locked = position_locked
        self.context_menu = QMenu(self.widget_parent)
        self.button = PlotButton(self.short_name, self, 'data.csv', 'Pressure', self.widget_parent)
        self.long_name_label = QLabel(self.widget_parent)
        self.short_name_label = CustomLabel(widget_parent=self.widget_parent, object_=self,
                                            is_vertical=self.is_vertical)
        self.long_name_label_position_num = long_name_label_position_num
        self.anchor_points = []

        self._initButton()
        self._initLabels()
        self._initAnchorPoints()

    def _initButton(self):
        """
        Basic function that handles all the setup for the PlotButton
        Should only be called from __init__
        """
        # Create Button and style it
        self.button.setStyleSheet("background-color:transparent;border:0;")
        self.button.setContextMenuPolicy(Qt.CustomContextMenu)
        self.button.setToolTip(self.short_name + "\nState: Closed")

        self.button.resize(self.width, self.height)
        self.button.move(self.position.x(), self.position.y())

        # Add quitAction
        self.context_menu.addAction("Delete Object")

        # Connect plot options to button context menu
        self.button.clicked.connect(lambda: self.onClick())
        self.button.customContextMenuRequested.connect(
            lambda *args: self.contextMenuEvent_(*args)
        )
        self.button.show()
        # Raise button above label
        self.button.raise_()

    def _initLabels(self):
        """
        Basic function that handles all the setup for the object label
        Should only be called from __init__
        """
        # Get font and set it
        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily("Arial")
        font.setPointSize(23 * self.gui.font_scale_ratio)


        #### Long Name Label ####
        # Sets the sizing of the label
        self.long_name_label.setFont(font)
        self.long_name_label.setFixedWidth(40 * 1.75 * self.widget_parent.gui.pixel_scale_ratio[0])
        self.long_name_label.setFixedHeight(80 * self.widget_parent.gui.pixel_scale_ratio[0])  # 80 Corresponds to three rows at this font type and size (Arial 23)
        self.long_name_label.setText(self.long_name)  # Solenoid long name
        self.long_name_label.setStyleSheet('color: white')
        self.long_name_label.setWordWrap(1)
        # Move the label into position
        self.setLongNameLabelPosition(self.long_name_label_position_num)
        # Sets alignment of label
        self.long_name_label.setAlignment(Qt.AlignCenter | Qt.AlignTop)

        #### Short Name Label ####
        font.setPointSize(10 * self.gui.font_scale_ratio)
        self.short_name_label.setFont(font)
        self.short_name_label.setText(self.short_name)
        self.short_name_label.setStyleSheet('color: white')

        self.short_name_label.setFixedSize_()

        if self.is_vertical:
            self.short_name_label.moveToPosition("Left")
        else:
            self.short_name_label.moveToPosition("Bottom")

        # Make em visible
        self.long_name_label.show()
        self.short_name_label.show()

    def _initAnchorPoints(self):
        """
        Inits the anchor points for the object
        Should only be called from __init__
        """
        # Default points are the midpoints of the four sides.
        anchor_points = [AnchorPoint(QPoint(int(self.width / 2), 0), self, parent=self.widget_parent),
                         AnchorPoint(QPoint(int(self.width / 2), self.height), self, parent=self.widget_parent),
                         AnchorPoint(QPoint(0, int(self.height / 2)), self, parent=self.widget_parent),
                         AnchorPoint(QPoint(self.width, int(self.height / 2)), self, parent=self.widget_parent)
                         ]
        self.anchor_points = anchor_points

    """----------------------------------------------------------------------------------------------------------------
    GETTERS and SETTERS
    ----------------------------------------------------------------------------------------------------------------"""


    def setToolTip_(self, text):
        """
        Sets the toolTip of the button
        :param text: text to be set on the tooltip
        """
        self.button.setToolTip(self.short_name + "\n" + text)

    def setLongName(self, name):
        """
        Sets long name and label of object
        :param name: long_name of the object
        """
        self.long_name = name
        self.long_name_label.setText(name)

    def setShortName(self, name):
        """
        Sets short name and label of object
        :param name: short_name of the object
        """
        self.short_name = name
        self.short_name_label.setText(name)

        # Moves the label to keep it in the center if it changes length
        self.short_name_label.moveToPosition()

    def setScale(self, scale):
        """
        Sets scale of the object, and moves origin to maintain same center position
        :param scale: scale on the object

        """

        # old_scale used for the factor to change size
        old_scale = self.scale
        self.scale = scale

        # The origin of objects is the top left corner, but to maintain alignment should be scaled from the center.
        # To achieve this, the old center and new center are calculated and the origin is offset to make sure the
        # center position always remains constant
        center_position = self.position + QPoint(int(self.width/2), int(self.height/2))
        scaled_center_position = self.position + QPoint(int((self.width*(self.scale/old_scale) / 2)), int((self.height*(self.scale/old_scale))/2))
        center_offset = scaled_center_position - center_position

        # Update object values accordingly
        self.width = self.width * (self.scale/old_scale)
        self.height = self.height * (self.scale/old_scale)
        self.button.resize(self.width, self.height)

        # Move things into the correct location
        self.move(QPointF(self.position).toPoint() - QPointF(center_offset).toPoint())
        self.button.move(self.position)

        # Update some other dependent values
        self.setAnchorPoints()

        # Tells widget painter to update screen
        self.widget_parent.update()

    def setAvionicsNumber(self, number):
        """
        Sets avionics number of object
        :param number: avionics number of the object
        """
        self.avionics_number = number

    def setFluid(self, fluid):
        """
        Sets fluid of object
        :param fluid: fluid of the object
        """
        self.fluid = Constants.fluid[fluid]

        # Tells widget painter to update screen
        self.widget_parent.update()

    def setPositionLock(self, is_locked: bool):
        """
        Sets if the position of on object is locked
        :param is_locked: is the position locked
        """

        self.position_locked = is_locked

    # TODO: Get rid of label_num and move over to a point based system
    def setLongNameLabelPosition(self, label_num: int, label_position: QPoint = None):
        """
        Sets the position of the long name label on an object
        :param label_num: num position of label -> Want to deprecate
        :param label_position: new position of label
        """
        self.long_name_label_position_num = label_num

        # If label position is not given, have label follow object
        if label_position is None:
            # Move the label into position
            self.long_name_label.move(self.position.x(), self.position.y())
        else:
            self.long_name_label.move(label_position.x(),label_position.y())

    def setAnchorPoints(self):
        """
        Sets the anchor points for the object. Called when object is created, and when scale changes
        """
        self.anchor_points[0].updateLocalPosition(QPoint(int(self.width/2) , 0                  ))
        self.anchor_points[1].updateLocalPosition(QPoint(int(self.width/2) , self.height        ))
        self.anchor_points[2].updateLocalPosition(QPoint(0                 , int(self.height/2) ))
        self.anchor_points[3].updateLocalPosition(QPoint(self.width        , int(self.height/2) ))

    """----------------------------------------------------------------------------------------------------------------
    OBJECT ACTIONS 
    ----------------------------------------------------------------------------------------------------------------"""

    def updateAnchorPoints(self):
        """
        Updates the position of the anchor points for the object. Called when object is moved
        SetAnchorPoints cannot be called when the object is moved, because alignment values will be reset
        """
        for ap in self.anchor_points:
            ap.updatePosition()

    def hideAnchorPoints(self):
        for ap in self.anchor_points:
            ap.hide()

    def showAnchorPoints(self):
        for ap in self.anchor_points:
            ap.show()

    def onClick(self):
        """
        When a object is clicked this function is called. This is base functionality, more functionality
        can be added by overriding this function in the child class
        """

        if self.widget_parent.window.is_editing:
            if self.is_being_edited:
                self.widget_parent.controlsPanel.removeEditingObjects(self)
            else:
                self.widget_parent.controlsPanel.removeAllEditingObjects()
                self.widget_parent.controlsPanel.addEditingObjects(self)

        # Tells widget painter to update screen
        self.widget_parent.update()

    def setMouseEventTransparency(self, should_be_transparent):
        """
        Sets the object and its labels to be mouse transparent or not. When transparent the mouse events are not
        triggered on the buttons/ labels
        """
        self.button.setAttribute(Qt.WA_TransparentForMouseEvents, should_be_transparent)
        self.long_name_label.setAttribute(Qt.WA_TransparentForMouseEvents, should_be_transparent)
        self.short_name_label.setAttribute(Qt.WA_TransparentForMouseEvents, should_be_transparent)
        # Right now does not set ap points as transparent to allow for them to be clicked on
        # for ap in self.anchor_points:
        #     ap.setAttribute(Qt.WA_TransparentForMouseEvents, should_be_transparent)

    def draw(self):
        """
        Draws the object. Will almost always be overridden, this exists to provide some default functionality,
        mainly anchor points
        """
        # Default pen qualities
        pen = QPen()
        pen.setWidth(Constants.line_width)
        pen.setColor(Constants.fluidColor[self.fluid])
        self.widget_parent.painter.setPen(pen)

        # While editing draws small anchor points (6x6 box) on the object to help user with alignment
        if self.widget_parent.window.is_editing:
            self.showAnchorPoints()
            for point in self.anchor_points:
                self.widget_parent.painter.setPen(pen)
                point.draw()
        else:
            self.hideAnchorPoints()

    def move(self, point: QPoint):
        """
        Move object to a new position
        :param point: point to move to
        """

        if self.position_locked is False and self.locked is False:
            self.button.move(point)
            self.context_menu.move(point)
            self.position = point
            self.updateAnchorPoints()
            self.setLongNameLabelPosition(self.long_name_label_position_num)
            self.short_name_label.moveToPosition()
            self.deleteConnectedTubes()

        # Tells widget painter to update screen
        self.widget_parent.update()

    def checkApAlignment(self, pos: QPoint = None):
        """
        Checks to see if object should snap into place based on anchor points.
        :param pos: The position of the BASE object. For example if you want to see if a certain object's aps are
                    aligned you would pass in the that objects position. NOTE: the pos argument is provided to allow for
                    checking of alignment and potential adjusting before move() is called. If you are not calling this
                    before a move() call you (most likely) can leave the pos blank. It will default to the objects
                    current position
        :return:    This function returns the objects pos after checking alignment. This is to allow the position to be
                    updated if it was snapped into place
        """

        if pos is None:
            pos = self.position

        # TODO: Think real hard about a better less costly solution to this. Currently runs Ok? though

        # Determines if the object should be 'snapped' into place
        # Triple for loop :(. First for loop runs through all anchor points on the object, then for every object
        # onscreen, checks to see if the current anchor point, is near another object anchor point
        for anchor_point in self.anchor_points:
            anchor_point.x_aligned = False
            anchor_point.y_aligned = False
            for obj in self.widget_parent.object_list:
                if obj is not self:
                    for obj_ap in obj.anchor_points:
                        if obj_ap.x() - 5 < anchor_point.x() < obj_ap.x() + 5 and abs(
                                pos.x() - self.position.x()) < 5:
                            pos = QPoint(obj_ap.x() + (self.position.x() - anchor_point.x()), pos.y())
                            anchor_point.x_aligned = True
                        if obj_ap.y() - 5 < anchor_point.y() < obj_ap.y() + 5 and abs(
                                pos.y() - self.position.y()) < 5:
                            pos = QPoint(pos.x(), obj_ap.y() + (self.position.y() - anchor_point.y()))
                            anchor_point.y_aligned = True

        return pos

    """----------------------------------------------------------------------------------------------------------------
    EVENTS 
    ----------------------------------------------------------------------------------------------------------------"""

    def contextMenuEvent_(self, event):
        """
        Handler for context menu. These menus hand-off data plotting to plot windows
        :param event: default event from pyqt
        :return:
        """

        action = self.context_menu.exec_(self.button.mapToGlobal(event))

        if action is not None:
            if action.text() == "Delete Object":
                self.widget_parent.deleteObject(self)

        # TODO: Re-implement this when plotting is ready
        # self.plotMenuActions = []
        # for plot in self.widget_parent.gui.plotWindow.plotList:
        #     action = QAction(plot.name)
        #     self.plotMenuActions.append(action)
        #
        #     self.plotMenuActions[-1].triggered.connect(
        #         lambda *args, p=plot: self.link_plot(p, button)
        #     )
        #
        #     menu.addAction(self.plotMenuActions[-1])
        #
        # menu.exec_(self.button.mapToGlobal(event))

    """----------------------------------------------------------------------------------------------------------------
    DELETION 
    ----------------------------------------------------------------------------------------------------------------"""

    def deleteSelf(self):
        """
        Called for object to delete itself
        """

        self.button.deleteLater()
        del self.button
        self.short_name_label.deleteLater()
        del self.short_name_label
        self.long_name_label.deleteLater()
        del self.long_name_label
        for ap in self.anchor_points:
            ap.deleteLater()
        del self.anchor_points
        del self._id
        del self.avionics_number
        del self

    def deleteConnectedTubes(self):
        """
        Called for object to attached tubes
        """

        for ap in self.anchor_points:
            if ap.tube is not None:
                self.widget_parent.tube_list.remove(ap.tube)
                del ap.tube
                ap.tube = None

        self.widget_parent.update()


    def link_plot(self, plot, button):
        """
        Link a Plot object to a given data file
        :param plot: plot object that needs a link to a data file
        :param button: button instance that was clicked on
        :return:
        """
        plot.link_data(button)


