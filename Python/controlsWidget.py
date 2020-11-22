from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants
from solenoid import Solenoid
from tank import Tank
from chamber import Chamber
from throttleValve import ThrottleValve
from threeWayValve import ThreeWayValve
from heatEx import HeatEx
from genSensor import GenSensor
from tube import Tube
from regulator import Regulator
from checkValve import CheckValve
from overrides import overrides

from termcolor import colored

import json

"""
This file contains the class to create the main controls widget (where the P&ID is)
"""


class ControlsWidget(QWidget):
    """
    Class that creates the Control Widget. This widget contains all the graphical representations of objects, that can
    also be interacted with
    """

    # Temp values
    # TODO: Properly implement these values
    screenWidthBuffer = 100
    screenHeightBuffer = 100

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
        self.object_type_list = [Solenoid, ThreeWayValve, Tank, GenSensor, Chamber,
                                 ThrottleValve, HeatEx, Regulator, CheckValve]

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

        # Var to keep track when a tube is being drawn
        self.is_drawing = False

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Constants.MASA_Blue_color)
        self.setPalette(p)

        # TODO: move these somewhere when file system is initiated
        self.loadData()

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
        pixmap = QPixmap('masawhiteworm3.png')
        pixmap = pixmap.scaled(300 * self.gui.pixel_scale_ratio[0], 100 * self.gui.pixel_scale_ratio[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.masa_logo.setPixmap(pixmap)

        if self.gui.platform == "OSX":
            self.masa_logo.setGeometry(10 * self.gui.pixel_scale_ratio[0], self.gui.screenResolution[1] -
                                       (100 * self.gui.pixel_scale_ratio[1]), 300 * self.gui.pixel_scale_ratio[0],
                                       100 * self.gui.pixel_scale_ratio[1])
        elif self.gui.platform == "Windows":
            self.masa_logo.setGeometry(10 * self.gui.pixel_scale_ratio[0], self.gui.screenResolution[1] -
                                   (200 * self.gui.pixel_scale_ratio[1]), 300 * self.gui.pixel_scale_ratio[0],
                                   100 * self.gui.pixel_scale_ratio[1])


    # TODO: Almost anything but this, that being said it works
    def finalizeInit(self):
        """
        There simply must be an elegant solution to this
        """
        self.controlsPanel = self.window.controlsPanelWidget

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
            self.controlsPanel.removeEditingObject()
            if self.parent.window.fileName != "":
                self.saveData(self.parent.window.fileName)
            else:
                self.parent.window.saveFileDialog()

        # Tells painter to update screen
        self.update()

    def deleteObject(self, object_):
        """
        Deletes an object

        :param object_: Object to delete
        """

        # Remove object from any tracker lists
        self.object_list.remove(object_)

        # Tells the object to delete itself
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
                    self.is_drawing = False
                    del tube
                    self.update()
        #If 'r' key is pressed:
        elif e.key() == 82:
            #Calls rotate method on last object in editing list
            if self.controlsPanel.object_editing is not None:
                self.controlsPanel.object_editing.rotate()
                self.update()


    @overrides
    def mousePressEvent(self, e:QMouseEvent):
        """"
        This event is called when the user is drawing a new line and wants to put 'bends' into the line
        """

        # Checks is tubes are being drawn and if so a blend is placed
        if self.is_drawing:
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
        # When an object is being dragged we don't want a mouse release event to trigger
        self.should_ignore_mouse_release = True

        # Checks if tubes are being drawn and if so updates the end position of the tube to be the mouse position
        if self.is_drawing:
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
            self.controlsPanel.removeEditingObject()
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
                self.controlsPanel.removeEditingObject()
                #TODO: I think this can be condensed with a for loop
                if action.text() == "New Solenoid":
                    self.object_list.append(Solenoid(self, position=point,fluid=0, is_vertical=0))
                elif action.text() == "New 3 Way Valve":
                    self.object_list.append(ThreeWayValve(self, position=point,fluid=0, is_vertical=0))
                elif action.text() == "New Tank":
                    self.object_list.append(Tank(self, position=point, fluid=0))
                elif action.text() == "New Generic Sensor":
                    self.object_list.append(GenSensor(self, position=point, fluid=0, is_vertical=0))
                elif action.text() == "New Chamber":
                    self.object_list.append(Chamber(self, position=point, fluid=4, is_vertical=1))
                elif action.text() == "New Throttle Valve":
                    self.object_list.append(ThrottleValve(self, position=point, fluid=0, is_vertical=0))
                elif action.text() == "New Heat Exchanger":
                    self.object_list.append(HeatEx(self, position=point, fluid=0, is_vertical=0))
                elif action.text() == "New Regulator":
                    self.object_list.append(Regulator(self, position=point, fluid=0, is_vertical=0))
                elif action.text() == "New Check Valve":
                    self.object_list.append(CheckValve(self, position=point, fluid=0, is_vertical=0))
                else:
                    print(colored("WARNING: Context menu has no action attached to " + action.text(), 'red'))

                self.controlsPanel.addEditingObject(self.object_list[-1])

            self.update()

    # HMM: Most likely in the future more than just object data will be saved so this function will need to be adjusted
    #  so it can pass along the saveDict. Similar to the TO-DO for load data
    def saveData(self, filename):
        """
        When the user requests data to be saved this function is called and handles saving all the data for objects that
        are currently drawn on screen. It simply requests save data from each individual object and compiles it into one
        dictionary and then saves it to a json
        """
        data = {}
        # For every object, get it save dictionary and compile it into one dictionary
        for obj in self.object_list:
            data = {**data, **(obj.generateSaveDict())}

        # For every tube, get it save dictionary and compile it into one dictionary
        for tube in self.tube_list:
            data = {**data, **(tube.generateSaveDict())}

        # With the open file, write to json with a tab as an indent
        with open(filename, "w") as write_file:
            json.dump(data, write_file, indent="\t")

    # TODO: This should not be the location that data is started the load from,
    #  ideally it would come from the top level GUI application and dispatch the data to where it needs to go
    def loadData(self, fileName="data_file.json"):
        """
        Loads data from a json file and populates the widget with all the saved objects
        """

        # Open and read the loaded json file
        with open(fileName, "r") as read_file:
            data = json.load(read_file)

        # TODO: I was really lazy so I just copy pasted but can be done nicer
        # Quickly parses json data dict and calls the right object initializer to add it to screen
        for i in data:
            if i.split()[0] == "Solenoid":
                sol = data[i]
                self.object_list.append(Solenoid(self, _id=sol["id"], position=QPoint(sol["pos"]["x"],sol["pos"]["y"]),
                                                 fluid=sol["fluid"],width=sol["width"], height=sol["height"],
                                                 name=sol["name"],scale=sol["scale"],
                                                 serial_number=sol["serial number"],
                                                 long_name=sol["long name"], is_vertical=sol["is vertical"],
                                                 locked=sol["is locked"],position_locked=sol["is pos locked"],
                                                 serial_number_label_pos=sol["serial number label"]["pos string"],
                                                 serial_number_label_font_size=sol["serial number label"]["font size"],
                                                 serial_number_label_local_pos=QPoint(sol["serial number label"]["local pos"]["x"],sol["serial number label"]["local pos"]["y"]),
                                                 long_name_label_pos=sol["long name label"]["pos string"],
                                                 long_name_label_font_size=sol["long name label"]["font size"],
                                                 long_name_label_local_pos=QPoint(sol["long name label"]["local pos"]["x"],sol["long name label"]["local pos"]["y"]),
                                                 long_name_label_rows=sol["long name label"]["rows"], channel_number=sol["channel number"]))

            if i.split()[0] == "Tank":
                tnk = data[i]
                self.object_list.append(Tank(self, _id=tnk["id"], position=QPoint(tnk["pos"]["x"], tnk["pos"]["y"]),
                                             fluid=tnk["fluid"], width=tnk["width"], height=tnk["height"],
                                             name=tnk["name"], scale=tnk["scale"],
                                             serial_number=tnk["serial number"],
                                             long_name=tnk["long name"], is_vertical=tnk["is vertical"],
                                             locked=tnk["is locked"], position_locked=tnk["is pos locked"],
                                             serial_number_label_pos=tnk["serial number label"]["pos string"],
                                             serial_number_label_font_size=tnk["serial number label"]["font size"],
                                             serial_number_label_local_pos=QPoint(tnk["serial number label"]["local pos"]["x"], tnk["serial number label"]["local pos"]["y"]),
                                             long_name_label_pos=tnk["long name label"]["pos string"],
                                             long_name_label_font_size=tnk["long name label"]["font size"],
                                             long_name_label_local_pos=QPoint(tnk["long name label"]["local pos"]["x"], tnk["long name label"]["local pos"]["y"]),
                                             long_name_label_rows=tnk["long name label"]["rows"]))

            if i.split()[0] + " " + i.split()[1] == "Generic Sensor":  # Truly a lazy mans fix
                pt = data[i]
                self.object_list.append(GenSensor(self, _id=pt["id"], position=QPoint(pt["pos"]["x"], pt["pos"]["y"]),
                                                 fluid=pt["fluid"], width=pt["width"], height=pt["height"],
                                                 name=pt["name"], scale=pt["scale"],
                                                 serial_number=pt["serial number"],
                                                 long_name=pt["long name"], is_vertical=pt["is vertical"],
                                                 locked=pt["is locked"], position_locked=pt["is pos locked"],
                                                 serial_number_label_pos=pt["serial number label"]["pos string"],
                                                 serial_number_label_font_size=pt["serial number label"]["font size"],
                                                 serial_number_label_local_pos=QPoint(pt["serial number label"]["local pos"]["x"], pt["serial number label"]["local pos"]["y"]),
                                                 long_name_label_pos=pt["long name label"]["pos string"],
                                                 long_name_label_font_size=pt["long name label"]["font size"],
                                                 long_name_label_local_pos=QPoint(pt["long name label"]["local pos"]["x"], pt["long name label"]["local pos"]["y"]),
                                                 long_name_label_rows=pt["long name label"]["rows"],
                                                 sensor_type=pt["sensor type"], channel_number=pt["channel number"]))
            
            if i.split()[0] == "Chamber":
                idx = data[i]
                self.object_list.append(Chamber(self, _id=idx["id"], position=QPoint(idx["pos"]["x"], idx["pos"]["y"]),
                                                fluid=idx["fluid"], width=idx["width"], height=idx["height"],
                                                name=idx["name"], scale=idx["scale"],
                                                serial_number=idx["serial number"],
                                                long_name=idx["long name"], is_vertical=idx["is vertical"],
                                                locked=idx["is locked"], position_locked=idx["is pos locked"],
                                                serial_number_label_pos=idx["serial number label"]["pos string"],
                                                serial_number_label_font_size=idx["serial number label"]["font size"],
                                                serial_number_label_local_pos=QPoint(idx["serial number label"]["local pos"]["x"], idx["serial number label"]["local pos"]["y"]),
                                                long_name_label_pos=idx["long name label"]["pos string"],
                                                long_name_label_font_size=idx["long name label"]["font size"],
                                                long_name_label_local_pos=QPoint(idx["long name label"]["local pos"]["x"], idx["long name label"]["local pos"]["y"]),
                                                long_name_label_rows=idx["long name label"]["rows"]))

            if i.split()[0] + " " + i.split()[1] == "Throttle Valve":  
                idx = data[i]
                self.object_list.append(ThrottleValve(self, _id=idx["id"], position=QPoint(idx["pos"]["x"],idx["pos"]["y"]),
                                                 fluid=idx["fluid"],width=idx["width"], height=idx["height"],
                                                 name=idx["name"],scale=idx["scale"],
                                                 serial_number=idx["serial number"],
                                                 long_name=idx["long name"], is_vertical=idx["is vertical"],
                                                 locked=idx["is locked"],position_locked=idx["is pos locked"],
                                                 serial_number_label_pos=idx["serial number label"]["pos string"],
                                                 serial_number_label_font_size=idx["serial number label"]["font size"],
                                                 serial_number_label_local_pos=QPoint(idx["serial number label"]["local pos"]["x"],idx["serial number label"]["local pos"]["y"]),
                                                 long_name_label_pos=idx["long name label"]["pos string"],
                                                 long_name_label_font_size=idx["long name label"]["font size"],
                                                 long_name_label_local_pos=QPoint(idx["long name label"]["local pos"]["x"],idx["long name label"]["local pos"]["y"]),
                                                 long_name_label_rows=idx["long name label"]["rows"]))
            
            if i.split()[0] + " " + i.split()[1] == "3 Way":  
                idx = data[i]
                self.object_list.append(ThreeWayValve(self, _id=idx["id"], position=QPoint(idx["pos"]["x"],idx["pos"]["y"]),
                                                 fluid=idx["fluid"],width=idx["width"], height=idx["height"],
                                                 name=idx["name"],scale=idx["scale"],
                                                 serial_number=idx["serial number"],
                                                 long_name=idx["long name"], is_vertical=idx["is vertical"],
                                                 locked=idx["is locked"],position_locked=idx["is pos locked"],
                                                 serial_number_label_pos=idx["serial number label"]["pos string"],
                                                 serial_number_label_font_size=idx["serial number label"]["font size"],
                                                 serial_number_label_local_pos=QPoint(idx["serial number label"]["local pos"]["x"],idx["serial number label"]["local pos"]["y"]),
                                                 long_name_label_pos=idx["long name label"]["pos string"],
                                                 long_name_label_font_size=idx["long name label"]["font size"],
                                                 long_name_label_local_pos=QPoint(idx["long name label"]["local pos"]["x"],idx["long name label"]["local pos"]["y"]),
                                                 long_name_label_rows=idx["long name label"]["rows"]))
            
            if i.split()[0] + " " + i.split()[1] == "Heat Exchanger":  
                idx = data[i]
                self.object_list.append(HeatEx(self, _id=idx["id"], position=QPoint(idx["pos"]["x"],idx["pos"]["y"]),
                                                 fluid=idx["fluid"],width=idx["width"], height=idx["height"],
                                                 name=idx["name"],scale=idx["scale"],
                                                 serial_number=idx["serial number"],
                                                 long_name=idx["long name"], is_vertical=idx["is vertical"],
                                                 locked=idx["is locked"],position_locked=idx["is pos locked"],
                                                 serial_number_label_pos=idx["serial number label"]["pos string"],
                                                 serial_number_label_font_size=idx["serial number label"]["font size"],
                                                 serial_number_label_local_pos=QPoint(idx["serial number label"]["local pos"]["x"],idx["serial number label"]["local pos"]["y"]),
                                                 long_name_label_pos=idx["long name label"]["pos string"],
                                                 long_name_label_font_size=idx["long name label"]["font size"],
                                                 long_name_label_local_pos=QPoint(idx["long name label"]["local pos"]["x"],idx["long name label"]["local pos"]["y"]),
                                                 long_name_label_rows=idx["long name label"]["rows"]))
                
            # TODO: Pass data to properly attach these to the right anchor point if applicable
            if i.split()[0] == "Tube":
                tube = data[i]
                # First pull all the point data out and put it in an array
                points = []
                for j in tube["bend positions"]:
                    points.append(QPoint(tube["bend positions"][j]["x"], tube["bend positions"][j]["y"]))

                self.tube_list.append(Tube(self, tube_id=tube["tube id"], fluid=tube["fluid"], points=points))



