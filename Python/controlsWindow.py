from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants
from csvHelper import CsvHelper
from solenoid import Solenoid
from tank import Tank
from pressureTransducer import PressureTransducer
from MathHelper import MathHelper
from controlsPanelWidget import  ControlsPanelWidget
from overrides import overrides

from termcolor import colored

"""
This file contains the class to create the window and widget
"""

class ControlsWindow(QMainWindow):
    """
    Window to house the controlsWidget
    """

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.gui = self.parent

        # Set geometry
        self.title = 'Controls Window'

        # Below numbers are arbitrary
        # TODO: Make them not arbitrary
        self.left = 0
        self.top = 0
        self.width = self.gui.screenResolution[0]
        self.height = self.gui.screenResolution[1]

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Width of the panel on the right hand side
        # HMM: Should this go here or in the ControlsPanelWidget Class?
        self.panel_width = 300 * self.gui.pixel_scale_ratio[0]

        # Marker for if the controls area is being edited
        self.is_editing = False


        self.controlsWidget = ControlsWidget(self)
        self.controlsPanelWidget = ControlsPanelWidget(self)

        # Some variables depend on the init of ControlsPanelWidget so has to happen after it inits
        self.controlsWidget.finalizeInit()

        self.showMaximized()

        self.show()

        # Menu shit that is not ready yet
        # exitAct = QAction('&Save', self)
        # exitAct.setStatusTip('Exit application')
        # exitAct.triggered.connect(qApp.quit)
        #
        # self.statusBar()
        # self.statusBar().showMessage('Ready')
        #
        # menubar = self.menuBar()
        # fileMenu = menubar.addMenu('&File')
        # fileMenu.addAction(exitAct)



class ControlsWidget(QWidget):
    """
    Class that creates the Control Widget. This widget contains all the graphical representations of objects, that can
    also be interacted with
    """

    # Temp values
    # TODO: Properly implement these values
    screenWidthBuffer = 100
    screenHeightBuffer = 100
    objectScale = 1.75 # This maybe should be a instance variable of all objects

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.window = parent
        self.gui = self.window.parent

        self.left = 0
        self.top = 0

        self.width = self.gui.screenResolution[0] - self.window.panel_width
        self.height = self.gui.screenResolution[1]

        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

        # Keeps track of all the different object types
        # Fun Fact you can call self.object_type_list[0](init vars) to create a new Solenoid Object
        self.object_type_list = [Solenoid, Tank, PressureTransducer]

        # Object Tracker
        self.object_list = []

        self.tube_list = []

        self.setMouseTracking(True)

        # painter controls the drawing of everything on the widget
        self.painter = QPainter()

        self.context_menu = QMenu(self)

        self.initContextMenu()

        # Var to keep track of the importance of mouse clicks
        self.should_ignore_mouse_release = False

        # Sets the color of the panel to dark Gray
        # TODO: Make this not look totally terrible
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.darkGray)
        self.setPalette(p)

        #self.initConfigFiles()
        #self.createObjects()


        # TODO: Move this button to the edit menu bar
        self.edit_button = QPushButton("EDIT", self)
        self.edit_button.clicked.connect(lambda: self.toggleEdit())
        self.edit_button.resize(70 * self.gui.pixel_scale_ratio[0], 30 * self.gui.pixel_scale_ratio[1])
        self.edit_button.move(self.gui.screenResolution[0] - self.window.panel_width - self.edit_button.width() - 30 * self.gui.pixel_scale_ratio[0],
                              30 * self.gui.pixel_scale_ratio[1])
        self.edit_button.show()

        # Masa Logo on bottom left of screen
        # FIXME: Make this not blurry as hell
        # TODO: Move this to the main window instead of the widget
        # TODO: Make CustomMainWindow Class to handle things like this for all windows
        self.masa_logo = QLabel(self)
        pixmap = QPixmap('masawhiteworm2.png')
        pixmap = pixmap.scaled(300 * self.gui.pixel_scale_ratio[0], 100 * self.gui.pixel_scale_ratio[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.masa_logo.setPixmap(pixmap)
        self.masa_logo.setGeometry(10 * self.gui.pixel_scale_ratio[0], self.gui.screenResolution[1] -
                                   (100 * self.gui.pixel_scale_ratio[1]), 300 * self.gui.pixel_scale_ratio[0],
                                   100 * self.gui.pixel_scale_ratio[1])


    # TODO: Almost anything but this, that being said it works
    def finalizeInit(self):
        """
        There simply must be an elegant solution to this
        """
        self.controlsPanel = self.window.controlsPanelWidget

    def initConfigFiles(self):
        """
        Loads in all the configuration files for the widget
        """

        self.csvObjectData = CsvHelper.loadCsv("csvObjectData.csv")

        # Map objects on screen to the screen resolution of the users screen.
        # This is a quick fix, this method messes with two objects that should be aligned
        # TODO: Change position scaling algorithm in such a way that maintains inter-object alignment
        # TODO: Move this loop somewhere else
        for i in range(self.csvObjectData[1]):
            self.csvObjectData[2][2][i] = MathHelper.mapValue(float(self.csvObjectData[2][2][i]), 139, 790, self.screenWidthBuffer, self.parent.parent.screenResolution[0]-self.screenWidthBuffer - 300)
            self.csvObjectData[2][3][i] = MathHelper.mapValue(float(self.csvObjectData[2][3][i]), 179, 590, self.screenHeightBuffer,self.parent.parent.screenResolution[1] - self.screenHeightBuffer)

    def createObjects(self):
        """
        Creates objects to be drawn onscreen. Uses csv file to load in all the object types, positions, and fluids
        """
        # Loops through all the cols of the csv

        for i in range(self.csvObjectData[1]):
            # Creates horizontal and vertical solenoids
            if int(self.csvObjectData[2][0][i]) == 0 or int(self.csvObjectData[2][0][i]) == 1:
                self.solenoid_list.append(
                    Solenoid(self, QPointF(float(self.csvObjectData[2][2][i]), float(self.csvObjectData[2][3][i])),
                             int(self.csvObjectData[2][1][i]), int(self.csvObjectData[2][0][i])))
            # Creates Tanks
            if int(self.csvObjectData[2][0][i]) == 2:
                self.tank_list.append(
                    Tank(self, QPointF(float(self.csvObjectData[2][2][i]), float(self.csvObjectData[2][3][i])),
                          int(self.csvObjectData[2][1][i])))


        self.pressure_transducer_list.append(PressureTransducer(self, QPointF(20, 300), 0, False))

    def initContextMenu(self):
        """
        Inits the context menu for when someone right clicks on the widget (background)
        """

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda *args: self.contextMenuEvent_(*args)) # *args passes point

        # For all the object types, create a right button action called "New 'Object Name'"
        for object_type in self.object_type_list:
            self.context_menu.addAction("New " + object_type.object_name)



    def toggleEdit(self):
        """
        Toggles if the window is in edit mode or not
        """
        self.window.is_editing = not self.window.is_editing

        if self.window.is_editing:
            self.edit_button.setText("SAVE")
        else:
            self.edit_button.setText("EDIT")
            self.controlsPanel.edit_frame.hide()
            self.controlsPanel.save()

        # Tells painter to update screen
        self.update()

    def deleteObject(self, object_):
        """
        Deletes an object

        :param object_: Object to delete
        """

        # Remove object from any tracker lists
        self.object_list.remove(object_)

        #Tells the object to delete itself
        object_.deleteSelf()

        self.update()

    @overrides
    def paintEvent(self, e):
        """
        This event is called automatically in the background by pyQt. It is used to update the drawing on screen
        This function calls the objects own drawing methods to perform the actual drawing calculations
        """
        self.painter.begin(self)

        # This makes the objects onscreen more crisp
        self.painter.setRenderHint(QPainter.HighQualityAntialiasing)

        # Default pen qualities
        pen = QPen()
        pen.setWidth(Constants.line_width)

        # Draw Solenoids
        for object_ in self.object_list:
            pen.setColor(Constants.fluidColor[object_.fluid])
            self.painter.setPen(pen)
            object_.draw()

        for tube in self.tube_list:
            tube.draw()

        self.painter.end()


    @overrides
    def keyPressEvent(self, e:QKeyEvent):
        """
        Called whenever the user presses a button on the keyboard
        :param e:
        :return:
        """
        # If the return key is pressed:
        if e.key() == Qt.Key_Return:
            for tube in self.tube_list:
                if tube.is_being_drawn:
                    tube.completeTube()
        # If the escape key is pressed:
        elif e.key() == Qt.Key_Escape:
            for tube in self.tube_list:
                if tube.is_being_drawn:
                    self.tube_list.remove(tube)
                    del tube
                    self.update()


    @overrides
    def mousePressEvent(self, e:QMouseEvent):
        """"
        This event is called when the user is drawing a new line and wants to put 'bends' into the line
        """
        for tube in self.tube_list:
            if tube.is_being_drawn:
                tube.setCurrentPos(e.pos())
                self.update()



    @overrides
    def mouseMoveEvent(self, e:QMouseEvent):
        """"
        This event is called when the mouse is moving on screen. This is just to keep internal track of when the user is
        moving an object.
        """
        # When an object is being dragged we dont want a mouse release event to trigger
        self.should_ignore_mouse_release = True

        for tube in self.tube_list:
            if tube.is_being_drawn:
                tube.updateCurrentPos(e.pos())
                self.update()



    @overrides
    def mouseReleaseEvent(self, e:QMouseEvent):
        """
        This event is called when the user clicks on the widget background, ie. no buttons, labels, etc.
        It tells the controls panel to removes all the editing objects and clear itself.
        """

        # If we are not expecting a release don't remove all objects
        if not self.should_ignore_mouse_release:
            self.controlsPanel.removeAllEditingObjects()
        else:
            self.should_ignore_mouse_release = False

        # Tells widget painter to update screen
        self.update()

    def contextMenuEvent_(self, point):
        """
        This event is called when the user right clicks on the widget background, ie. no buttons, labels, etc.
        and selects an action. This function is called both in edit and non-edit mode.

        :param point: point where right click occurred
        """

        # If window is in edit mode
        if self.window.is_editing:
            action = self.context_menu.exec_(self.mapToGlobal(point))

            # Below ifs creates new objects at the point where the right click
            if action is not None:
                self.controlsPanel.removeAllEditingObjects()

                if action.text() == "New Solenoid":
                    self.object_list.append(Solenoid(self, point, 0, 0))
                elif action.text() == "New Tank":
                    self.object_list.append(Tank(self, point, 0))
                elif action.text() == "New Pressure Transducer":
                    self.object_list.append(PressureTransducer(self, point, 0, 0))
                else:
                    print(colored("WARNING: Context menu has no action attached to " + action.text(), 'red'))

                self.controlsPanel.addEditingObjects(self.object_list[-1])

            self.update()


