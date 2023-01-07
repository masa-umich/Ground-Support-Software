from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants
from object import BaseObject
from solenoid import Solenoid
from tank import Tank
from chamber import Chamber
from throttleValve import ThrottleValve
from threeWayValve import ThreeWayValve
from heatEx import HeatEx
from genSensor import GenSensor
from motor import Motor
from tube import Tube
from regulator import Regulator
from checkValve import CheckValve
from overrides import overrides
#from datetime import datetime

from termcolor import colored
from bidict import bidict
import os

import json
import traceback

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
        self.centralWidget = parent
        self.window = parent.window
        self.gui = parent.gui

        self.interface = self.window.interface
        self.channels = self.interface.channels

        self.left = 0
        self.top = 0

        self.width = self.gui.screenResolution[0] - self.parent.panel_width
        self.height = self.parent.height

        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

        # Keeps track of all the different object types
        # Fun Fact you can call self.object_type_list[0](init vars) to create a new Solenoid Object
        self.object_type_list = [Solenoid, Tank, Motor, GenSensor, ThreeWayValve, Chamber,
                                 ThrottleValve, HeatEx, Regulator, CheckValve]

        # Object Tracker
        self.object_list: [BaseObject] = []
        self.avionics_mappings = bidict({})
        self.object_count = {}

        for obj in self.object_type_list:
            self.object_count[obj.object_name] = 0

        # Object Id Tracker
        self.last_object_id = 0

        # Tube tracker
        self.tube_list = []

        self.last_tube_id = 0

        self.setMouseTracking(True)

        # painter controls the drawing of everything on the widget
        self.painter = QPainter()

        self.context_menu = QMenu(self)

        self.initContextMenu()

        # Var to keep track of the importance of mouse clicks
        self.should_ignore_mouse_release = False
        self.shouldSnap = True

        # Var to keep track when a tube is being drawn
        self.is_drawing = False

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Constants.MASA_Blue_color)
        self.setPalette(p)

        # Sidebar Abort Button Config
        self.main_abort_button = QPushButton(self)
        self.main_abort_button.setText("Abort")
        self.main_abort_button.setDefault(False)
        self.main_abort_button.setAutoDefault(False)

        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.monospace_font)
        font.setPointSize(50 * self.gui.font_scale_ratio)

        self.main_abort_button.setFont(font)
        self.main_abort_button.setFixedWidth(200 * self.gui.pixel_scale_ratio[0])
        self.main_abort_button.setStyleSheet("background-color : darkred")
        self.main_abort_button.setDisabled(False)
        self.main_abort_button.setFixedHeight(90 * self.gui.pixel_scale_ratio[1])
        self.main_abort_button.move(self.width - self.main_abort_button.width() - 20 * self.gui.pixel_scale_ratio[0], self.height - self.main_abort_button.height() - 20 * self.gui.pixel_scale_ratio[1])
        self.main_abort_button.show()

        self.gui.liveDataHandler.updateScreenSignal.connect(self.update)
        self.window.button_box.softwareAbortSoftArmedSignal.connect(self.setAbortButtonState)

        # TODO: move these somewhere when file system is initiated
        #self.loadData()

        # Masa Logo on bottom left of screen
        # FIXME: Make this not blurry as hell
        # TODO: Move this to the main window instead of the widget
        # TODO: Make CustomMainWindow Class to handle things like this for all windows
        self.masa_logo = QLabel(self)
        pixmap = QPixmap(self.gui.LAUNCH_DIRECTORY+'Images/masawhiteworm3.png')
        pixmap = pixmap.scaled(300 * self.gui.pixel_scale_ratio[0], 100 * self.gui.pixel_scale_ratio[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.masa_logo.setPixmap(pixmap)

        if self.gui.platform == "OSX":
            self.masa_logo.setGeometry(10 * self.gui.pixel_scale_ratio[0], self.height -
                                       (100 * self.gui.pixel_scale_ratio[1]), 300 * self.gui.pixel_scale_ratio[0],
                                       100 * self.gui.pixel_scale_ratio[1])
        elif self.gui.platform == "Windows":
            self.masa_logo.setGeometry(10 * self.gui.pixel_scale_ratio[0], self.height -
                                   (100 * self.gui.pixel_scale_ratio[1]), 300 * self.gui.pixel_scale_ratio[0],
                                   100 * self.gui.pixel_scale_ratio[1])

    # TODO: Almost anything but this, that being said it works
    def finalizeInit(self):
        """
        There simply must be an elegant solution to this
        """
        self.controlsPanel = self.parent.controlsPanelWidget
        self.main_abort_button.clicked.connect(self.centralWidget.controlsSidebarWidget.abort_init)

    def initContextMenu(self):
        """
        Inits the context menu for when someone right clicks on the widget (background)
        """

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda *args: self.contextMenuEvent_(*args)) # *args passes point

        # For all the object types, create a right button action called "New 'Object Name'"
        for object_type in self.object_type_list:
            self.context_menu.addAction("New " + object_type.object_name)

        self.context_menu.addAction("New Tube")

    def toggleEdit(self):
        """
        Toggles if the window is in edit mode or not
        """
        self.parent.is_editing = not self.parent.is_editing

        # Leaving edit mode, nothing to do when entering
        if not self.centralWidget.is_editing:
            if self.window.fileName != "":
                self.saveData(self.parent.window.fileName)
            else:
                self.window.saveFileDialog()

            self.controlsPanel.removeAllEditingObjects()

            # Prevents tube from drawing in run mode
            if self.is_drawing:
                for tube in self.tube_list:
                    if tube.is_being_drawn:
                        tube.completeTube()

        # Tells painter to update screen
        self.update()

    def deleteObject(self, object_):
        """
        Deletes an object

        :param object_: Object to delete
        """

        # Remove object from any tracker lists
        self.object_list.remove(object_)

        if object_ in self.centralWidget.controlsPanelWidget.editing_object_list:
            self.centralWidget.controlsPanelWidget.editing_object_list.remove(object_)

        # Tells the object to delete itself
        object_.deleteSelf()

        self.update()

    def moveObjectGroup(self, dif):
        """
        Moves a group of editing objects to a new position
        :param dif: this is the the difference to move each object, the relative distance essentially
        """

        # For every object in the group, move them
        for obj in self.centralWidget.controlsPanelWidget.editing_object_list:
            obj.move(dif + obj.position)

    def setObjectsMouseTransparency(self, isTransparent: bool):
        """
        For all objects drawn onscreen, set the objects mouse transparency. Mouse events will not be
        triggered if an object is transparent
        :param isTransparent: should the objects be transparent, True/ False
        """

        for obj in self.object_list:
            obj.setMouseEventTransparency(isTransparent)

    def resetObjectsAnchorPointAlignment(self):
        """
        Resets all objects anchor point alignment, basically prevents lines from being accidentally drawn once a
        process is done
        """
        for obj in self.object_list:
            for obj_ap in obj.anchor_points:
                obj_ap.x_aligned = False
                obj_ap.y_aligned = False

    # TODO: Double check what is said below is actually done
    @pyqtSlot(bool)
    def setAbortButtonState(self, softArmed: bool):
        """
        Sets the abort button in the bottom right corner as soft armed. Allows the user to click it when soft armed,
        but it may not cause an abort unless the gui is in an autosequence
        :param softArmed: bool, true if the button is soft armed
        """
        if softArmed:
            # if the button is enabled from the "Abort Button" settings menu
            self.main_abort_button.setStyleSheet("background-color : darkred")
            self.main_abort_button.setDisabled(False)
        else:  # button is disabled
            self.main_abort_button.setStyleSheet("color : gray")
            self.main_abort_button.setDisabled(True)

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
    def keyPressEvent(self, e: QKeyEvent):
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
                    tube.deleteTube()
                    self.resetObjectsAnchorPointAlignment()
                    self.update()
                    self.gui.setStatusBarMessage("Tube canceled")
        # If 'r' key is pressed:
        elif e.key() == Qt.Key_R:
            # Calls rotate method on last object in editing list
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

    def checkCursorWithinObject(self, e_pos):
        """
        This function determines if the cursor is inside an object. It is intended to be used when objects are set to be
        mouse transparent so no tooltip checks can be made
        :param e_pos: Event position of a cursor move event
        :return: The object that the current cursor position is in
        """

        largest_obj = None
        largest_obj_width = 0

        for obj in self.object_list:
            x1 = obj.position.x()
            y1 = obj.position.y()
            x2 = x1 + obj.width
            y2 = y1 + obj.height

            if x1 <= e_pos.x() <= x2 and y1 <= e_pos.y() <= y2:
                if largest_obj is None:
                    largest_obj = obj
                    largest_obj_width = obj.width
                elif largest_obj_width < obj.width:
                    largest_obj = obj
                    largest_obj_width = obj.width

        return largest_obj

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

                    # Check what objects the cursor is in and the tube, if they are inside the same object then clip the
                    # tube to be at the edge of that object.
                    if len(tube.points) > 0:
                        last_point = tube.points[-2]

                        curs_obj = self.checkCursorWithinObject(e.pos())
                        tube_obj = self.checkCursorWithinObject(tube.points[-1])

                        # Tube clip logic check:
                        if curs_obj is not None and curs_obj == tube_obj:
                            if tube.draw_direction == "Vertical":
                                if last_point.y() <= curs_obj.position.y():
                                    tube.updateCurrentPos(QPointF(last_point.x(), curs_obj.position.y()))
                                else:
                                    tube.updateCurrentPos(QPointF(last_point.x(), curs_obj.position.y() + curs_obj.height))
                            else:
                                if last_point.x() <= curs_obj.position.x():
                                    tube.updateCurrentPos(QPointF(curs_obj.position.x(), last_point.y()))
                                else:
                                    tube.updateCurrentPos(QPointF(curs_obj.position.x() + curs_obj.width, last_point.y()))

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
        if self.parent.is_editing and not self.is_drawing:
            action = self.context_menu.exec_(self.mapToGlobal(point))

            # Below ifs creates new objects at the point where the right click
            if action is not None:
                point = self.centralWidget.mapToGlobal(point)
                if self.gui.platform == "OSX" and self.window.isFullScreen():
                    point = point - self.window.pos()
                elif self.gui.platform == "Windows" and self.window.isFullScreen():
                    point = point - self.window.pos() - self.window.central_widget_offset + self.centralWidget.pos()
                else:
                    point = point - self.window.central_widget_offset - self.window.pos()
                # TODO: This is a suppppppper janky fix but it works
                point = QPointF(point.x() / self.gui.pixel_scale_ratio[0], point.y() / self.gui.pixel_scale_ratio[1])

                #TODO: I think this can be condensed with a for loop
                if action.text() == "New Solenoid":
                    self.object_count["Solenoid"] = self.object_count["Solenoid"]+1
                    self.object_list.append(Solenoid(self, position=point,fluid=0, is_vertical=False))
                elif action.text() == "New 3 Way Valve":
                    self.object_count["3 Way Valve"] = self.object_count["3 Way Valve"] + 1
                    self.object_list.append(ThreeWayValve(self, position=point,fluid=0, is_vertical=False))
                elif action.text() == "New Tank":
                    self.object_count["Tank"] = self.object_count["Tank"] + 1
                    self.object_list.append(Tank(self, position=point, fluid=False, override_indicator=False))
                elif action.text() == "New Generic Sensor":
                    self.object_count["Generic Sensor"] = self.object_count["Generic Sensor"] + 1
                    self.object_list.append(GenSensor(self, position=point, fluid=0, is_vertical=False))
                elif action.text() == "New Motor":
                    self.object_count["Motor"] = self.object_count["Motor"] + 1
                    self.object_list.append(Motor(self, position=point, fluid=0, is_vertical=False))
                elif action.text() == "New Chamber":
                    self.object_count["Chamber"] = self.object_count["Chamber"] + 1
                    self.object_list.append(Chamber(self, position=point, fluid=4, is_vertical=True))
                elif action.text() == "New Throttle Valve":
                    self.object_count["Throttle Valve"] = self.object_count["Throttle Valve"] + 1
                    self.object_list.append(ThrottleValve(self, position=point, fluid=0, is_vertical=False))
                elif action.text() == "New Heat Exchanger":
                    self.object_count["Heat Exchanger"] = self.object_count["Heat Exchanger"] + 1
                    self.object_list.append(HeatEx(self, position=point, fluid=0, is_vertical=False))
                elif action.text() == "New Regulator":
                    self.object_count["Regulator"] = self.object_count["Regulator"] + 1
                    self.object_list.append(Regulator(self, position=point, fluid=0, is_vertical=False))
                elif action.text() == "New Check Valve":
                    self.object_count["Check Valve"] = self.object_count["Check Valve"] + 1
                    self.object_list.append(CheckValve(self, position=point, fluid=0, is_vertical=False))
                elif action.text() == "New Tube":
                    self.tube_list.append(Tube(self, [],Constants.fluid["HE"], [self]))
                    self.setMouseTracking(True)
                else:
                    print(colored("WARNING: Context menu has no action attached to " + action.text(), 'red'))

                # Add editing object, and move back because the position is scaled and I am lazy
                if action.text() == "New Tube":
                    self.is_drawing = True
                    self.tube_list[-1].is_being_drawn = True
                else:
                    #mod = QApplication.keyboardModifiers()
                    self.controlsPanel.addEditingObject(self.object_list[-1])
                    self.object_list[-1].move(point)

                self.gui.setStatusBarMessage(action.text() + " created")

            self.update()

    def generateSensorMappingsToSend(self):
        """
        Similar to showSensorMappings, but instead makes a dictionary to send the data to the server
        :return: mapDict: a dictionary of sensor mappings for the server to save with the campaign
        """
        boardNames = []
        for board in self.centralWidget.controlsSidebarWidget.board_objects:
            boardNames.append(board.name)

        mapDict = {"Boards": boardNames}

        counter = 0
        for object_ in self.object_list:
            if hasattr(object_, "channel") and object_.isAvionicsFullyDefined():
                if object_.object_name != "Generic Sensor":
                    mapDict[counter] = [object_.long_name, self.window.interface.getPrefix(object_.avionics_board) + Constants.object_prefix_map[object_.name] + object_.channel]
                else:
                    mapDict[counter] = [object_.long_name, object_.channel]
                counter += 1

        return mapDict

    def showSensorMappings(self):
        """
        Compiles a list of sensor mappings, ie what channel things are plugged into. Puts it into a temporary file and
        opens that
        """

        with open("data/.tempMappings.txt", "w") as write_file:
            write_file.write("CONNECTED BOARDS:\n---------------------------------------------------------\n")
            for board in self.centralWidget.controlsSidebarWidget.board_objects:
                write_file.write(board.name + "\n")

            write_file.write("\n" + f'{"NAME":<25}{"CHANNEL":<12}' + "\n---------------------------------------------------------\n")
            for object_ in self.object_list:
                if hasattr(object_, 'channel') and object_.channel != "Undefined":
                    if object_.object_name != "Generic Sensor":
                        write_file.write(f'{object_.long_name + ",":<40}{self.window.interface.getPrefix(object_.avionics_board) + Constants.object_prefix_map[object_.name] +  object_.channel:<12}' + "\n")
                    else:
                        write_file.write(f'{object_.long_name + ",":<40}{object_.channel:<12}' + "\n")

        if self.gui.platform == "Windows":
            os.system('notepad data/.tempMappings.txt')
        elif self.gui.platform == "OSX":
            os.system('open -e data/.tempMappings.txt')
        else:
            print(colored("WARNING: System not supported. Manually open sensor mappings under data/.tempMappings", 'red'))

    def generateConfigurationSaveData(self):
        """
        When the user requests data to be saved this function is called and handles saving all the data for objects that
        are currently drawn on screen. It simply requests save data from each individual object and compiles it into one
        dictionary
        :return: dictionary of data
        """
        data = {}
        # For every object, get it save dictionary and compile it into one dictionary
        for obj in self.object_list:
            data = {**data, **(obj.generateSaveDict())}

        # For every tube, get it save dictionary and compile it into one dictionary
        for tube in self.tube_list:
            data = {**data, **(tube.generateSaveDict())}

        data = {**data, **(self.centralWidget.controlsSidebarWidget.generateSaveDict())}

        return data

    # HMM: Most likely in the future more than just object data will be saved so this function will need to be adjusted
    #  so it can pass along the saveDict. Similar to the TO-DO for load data
    def saveData(self, filename):
        """
        Saves generated dictionary data to json
        """

        data = {"VERSION": Constants.GUI_VERSION}

        data = {**data, **(self.generateConfigurationSaveData())}

        try:
            # With the open file, write to json with a tab as an indent
            with open(filename, "w") as write_file:
                json.dump(data, write_file, indent="\t")

            self.gui.setStatusBarMessage("Configuration saved to " + filename)

        except PermissionError:
            self.window.showStandardMessageDialog("Cannot Save File", "The file you are saving to is locked, or you do not have permission. Please use 'Save As' if you wish to modify", "Warning")
            self.gui.setStatusBarMessage("Edit permission denied for file: " + filename)


    # TODO: This should not be the location that data is started the load from,
    #  ideally it would come from the top level GUI application and dispatch the data to where it needs to go
    def loadData(self, fileName="data_file.json"):
        """
        Loads data from a json file and populates the widget with all the saved objects
        """

        # Open and read the loaded json file
        with open(fileName, "r") as read_file:
            data = json.load(read_file)

        boards = []

        # TODO: Move this out of controls widget
        # TODO: I was really lazy so I just copy pasted but can be done nicer
        # Quickly parses json data dict and calls the right object initializer to add it to screen
        for i in data:
            obj_type = i.rsplit(' ', 1)[0]

            if obj_type in self.object_count.keys():
                self.object_count[obj_type] = self.object_count[obj_type] + 1

            if obj_type == "Solenoid":
                sol = data[i]
                self.object_list.append(Solenoid(self, _id=sol["id"], position=QPointF(sol["pos"]["x"],sol["pos"]["y"]),
                                                 fluid=sol["fluid"],width=sol["width"], height=sol["height"],
                                                 name=sol["name"],scale=sol["scale"],
                                                 serial_number=sol["serial number"],
                                                 long_name=sol["long name"], is_vertical=sol["is vertical"],
                                                 locked=sol["is locked"],position_locked=sol["is pos locked"],
                                                 serial_number_label_pos=sol["serial number label"]["pos string"],
                                                 serial_number_label_font_size=sol["serial number label"]["font size"],
                                                 serial_number_label_local_pos=QPointF(sol["serial number label"]["local pos"]["x"],sol["serial number label"]["local pos"]["y"]),
                                                 long_name_label_pos=sol["long name label"]["pos string"],
                                                 long_name_label_font_size=sol["long name label"]["font size"],
                                                 long_name_label_local_pos=QPointF(sol["long name label"]["local pos"]["x"],sol["long name label"]["local pos"]["y"]),
                                                 long_name_label_rows=sol["long name label"]["rows"], channel=sol["channel"], board=sol["board"],
                                                 normally_open=sol['normally open'],long_name_visible=sol["long name label"]["is visible"],
                                                 serial_number_visible=sol["serial number label"]["is visible"]))

            elif obj_type == "Tank":
                tnk = data[i]
                self.object_list.append(Tank(self, _id=tnk["id"], position=QPointF(tnk["pos"]["x"], tnk["pos"]["y"]),
                                             fluid=tnk["fluid"], width=tnk["width"], height=tnk["height"],
                                             name=tnk["name"], scale=tnk["scale"],
                                             serial_number=tnk["serial number"],
                                             long_name=tnk["long name"], is_vertical=tnk["is vertical"],
                                             locked=tnk["is locked"], position_locked=tnk["is pos locked"],
                                             serial_number_label_pos=tnk["serial number label"]["pos string"],
                                             serial_number_label_font_size=tnk["serial number label"]["font size"],
                                             serial_number_label_local_pos=QPointF(tnk["serial number label"]["local pos"]["x"], tnk["serial number label"]["local pos"]["y"]),
                                             long_name_label_pos=tnk["long name label"]["pos string"],
                                             long_name_label_font_size=tnk["long name label"]["font size"],
                                             long_name_label_local_pos=QPointF(tnk["long name label"]["local pos"]["x"], tnk["long name label"]["local pos"]["y"]),
                                             long_name_label_rows=tnk["long name label"]["rows"],long_name_visible=tnk["long name label"]["is visible"],
                                             serial_number_visible=tnk["serial number label"]["is visible"], board=tnk["board"], channel=tnk["channel"]))
            elif obj_type == "Motor":
                motor = data[i]
                self.object_list.append(Motor(self, _id=motor["id"], position=QPointF(motor["pos"]["x"],motor["pos"]["y"]),
                                                 fluid=motor["fluid"],width=motor["width"], height=motor["height"],
                                                 name=motor["name"],scale=motor["scale"],
                                                 serial_number=motor["serial number"],
                                                 long_name=motor["long name"], is_vertical=motor["is vertical"],
                                                 locked=motor["is locked"],position_locked=motor["is pos locked"],
                                                 serial_number_label_pos=motor["serial number label"]["pos string"],
                                                 serial_number_label_font_size=motor["serial number label"]["font size"],
                                                 serial_number_label_local_pos=QPointF(motor["serial number label"]["local pos"]["x"],motor["serial number label"]["local pos"]["y"]),
                                                 long_name_label_pos=motor["long name label"]["pos string"],
                                                 long_name_label_font_size=motor["long name label"]["font size"],
                                                 long_name_label_local_pos=QPointF(motor["long name label"]["local pos"]["x"],motor["long name label"]["local pos"]["y"]),
                                                 long_name_label_rows=motor["long name label"]["rows"], channel=motor["channel"], board=motor["board"],long_name_visible=motor["long name label"]["is visible"],
                                                 serial_number_visible=motor["serial number label"]["is visible"]))

            elif obj_type == "Generic Sensor":
                pt = data[i]
                self.object_list.append(GenSensor(self, _id=pt["id"], position=QPointF(pt["pos"]["x"], pt["pos"]["y"]),
                                                 fluid=pt["fluid"], width=pt["width"], height=pt["height"],
                                                 name=pt["name"], scale=pt["scale"],
                                                 serial_number=pt["serial number"],
                                                 long_name=pt["long name"], is_vertical=pt["is vertical"],
                                                 locked=pt["is locked"], position_locked=pt["is pos locked"],
                                                 serial_number_label_pos=pt["serial number label"]["pos string"],
                                                 serial_number_label_font_size=pt["serial number label"]["font size"],
                                                 serial_number_label_local_pos=QPointF(pt["serial number label"]["local pos"]["x"], pt["serial number label"]["local pos"]["y"]),
                                                 long_name_label_pos=pt["long name label"]["pos string"],
                                                 long_name_label_font_size=pt["long name label"]["font size"],
                                                 long_name_label_local_pos=QPointF(pt["long name label"]["local pos"]["x"], pt["long name label"]["local pos"]["y"]),
                                                 long_name_label_rows=pt["long name label"]["rows"],
                                                 channel=pt["channel"],board=pt["board"],long_name_visible=pt["long name label"]["is visible"],
                                                 serial_number_visible=pt["serial number label"]["is visible"]))
            
            elif obj_type == "Chamber":
                idx = data[i]
                self.object_list.append(Chamber(self, _id=idx["id"], position=QPointF(idx["pos"]["x"], idx["pos"]["y"]),
                                                fluid=idx["fluid"], width=idx["width"], height=idx["height"],
                                                name=idx["name"], scale=idx["scale"],
                                                serial_number=idx["serial number"],
                                                long_name=idx["long name"], is_vertical=idx["is vertical"],
                                                locked=idx["is locked"], position_locked=idx["is pos locked"],
                                                serial_number_label_pos=idx["serial number label"]["pos string"],
                                                serial_number_label_font_size=idx["serial number label"]["font size"],
                                                serial_number_label_local_pos=QPointF(idx["serial number label"]["local pos"]["x"], idx["serial number label"]["local pos"]["y"]),
                                                long_name_label_pos=idx["long name label"]["pos string"],
                                                long_name_label_font_size=idx["long name label"]["font size"],
                                                long_name_label_local_pos=QPointF(idx["long name label"]["local pos"]["x"], idx["long name label"]["local pos"]["y"]),
                                                long_name_label_rows=idx["long name label"]["rows"],long_name_visible=idx["long name label"]["is visible"],
                                                 serial_number_visible=idx["serial number label"]["is visible"]))

            elif obj_type == "Throttle Valve":
                idx = data[i]
                self.object_list.append(ThrottleValve(self, _id=idx["id"], position=QPointF(idx["pos"]["x"],idx["pos"]["y"]),
                                                 fluid=idx["fluid"],width=idx["width"], height=idx["height"],
                                                 name=idx["name"],scale=idx["scale"],
                                                 serial_number=idx["serial number"],
                                                 long_name=idx["long name"], is_vertical=idx["is vertical"],
                                                 locked=idx["is locked"],position_locked=idx["is pos locked"],
                                                 serial_number_label_pos=idx["serial number label"]["pos string"],
                                                 serial_number_label_font_size=idx["serial number label"]["font size"],
                                                 serial_number_label_local_pos=QPointF(idx["serial number label"]["local pos"]["x"],idx["serial number label"]["local pos"]["y"]),
                                                 long_name_label_pos=idx["long name label"]["pos string"],
                                                 long_name_label_font_size=idx["long name label"]["font size"],
                                                 long_name_label_local_pos=QPointF(idx["long name label"]["local pos"]["x"],idx["long name label"]["local pos"]["y"]),
                                                 long_name_label_rows=idx["long name label"]["rows"],long_name_visible=idx["long name label"]["is visible"],
                                                 serial_number_visible=idx["serial number label"]["is visible"]))
            
            elif obj_type == "3 Way":
                idx = data[i]
                self.object_list.append(ThreeWayValve(self, _id=idx["id"], position=QPointF(idx["pos"]["x"],idx["pos"]["y"]),
                                                 fluid=idx["fluid"],width=idx["width"], height=idx["height"],
                                                 name=idx["name"],scale=idx["scale"],
                                                 serial_number=idx["serial number"],
                                                 long_name=idx["long name"], is_vertical=idx["is vertical"],
                                                 locked=idx["is locked"],position_locked=idx["is pos locked"],
                                                 serial_number_label_pos=idx["serial number label"]["pos string"],
                                                 serial_number_label_font_size=idx["serial number label"]["font size"],
                                                 serial_number_label_local_pos=QPointF(idx["serial number label"]["local pos"]["x"],idx["serial number label"]["local pos"]["y"]),
                                                 long_name_label_pos=idx["long name label"]["pos string"],
                                                 long_name_label_font_size=idx["long name label"]["font size"],
                                                 channel=idx["channel"], board=idx["board"],
                                                 long_name_label_local_pos=QPointF(idx["long name label"]["local pos"]["x"],idx["long name label"]["local pos"]["y"]),
                                                 long_name_label_rows=idx["long name label"]["rows"]))
            
            elif obj_type == "Heat Exchanger":
                idx = data[i]
                self.object_list.append(HeatEx(self, _id=idx["id"], position=QPointF(idx["pos"]["x"],idx["pos"]["y"]),
                                                 fluid=idx["fluid"],width=idx["width"], height=idx["height"],
                                                 name=idx["name"],scale=idx["scale"],
                                                 serial_number=idx["serial number"],
                                                 long_name=idx["long name"], is_vertical=idx["is vertical"],
                                                 locked=idx["is locked"],position_locked=idx["is pos locked"],
                                                 serial_number_label_pos=idx["serial number label"]["pos string"],
                                                 serial_number_label_font_size=idx["serial number label"]["font size"],
                                                 serial_number_label_local_pos=QPointF(idx["serial number label"]["local pos"]["x"],idx["serial number label"]["local pos"]["y"]),
                                                 long_name_label_pos=idx["long name label"]["pos string"],
                                                 long_name_label_font_size=idx["long name label"]["font size"],
                                                 long_name_label_local_pos=QPointF(idx["long name label"]["local pos"]["x"],idx["long name label"]["local pos"]["y"]),
                                                 long_name_label_rows=idx["long name label"]["rows"]))

            elif obj_type == "Regulator":
                idx = data[i]
                self.object_list.append(Regulator(self, _id=idx["id"], position=QPointF(idx["pos"]["x"], idx["pos"]["y"]),
                                               fluid=idx["fluid"], width=idx["width"], height=idx["height"],
                                               name=idx["name"], scale=idx["scale"],
                                               serial_number=idx["serial number"],
                                               long_name=idx["long name"], is_vertical=idx["is vertical"],
                                               locked=idx["is locked"], position_locked=idx["is pos locked"],
                                               serial_number_label_pos=idx["serial number label"]["pos string"],
                                               serial_number_label_font_size=idx["serial number label"]["font size"],
                                               serial_number_label_local_pos=QPointF(
                                                   idx["serial number label"]["local pos"]["x"],
                                                   idx["serial number label"]["local pos"]["y"]),
                                               long_name_label_pos=idx["long name label"]["pos string"],
                                               long_name_label_font_size=idx["long name label"]["font size"],
                                               long_name_label_local_pos=QPointF(
                                                   idx["long name label"]["local pos"]["x"],
                                                   idx["long name label"]["local pos"]["y"]),
                                               long_name_label_rows=idx["long name label"]["rows"]))

            # TODO: Pass data to properly attach these to the right anchor point if applicable
            elif obj_type == "Tube":
                tube = data[i]
                # First pull all the point data out and put it in an array
                points = []
                for j in tube["bend positions"]:
                    points.append(QPointF(tube["bend positions"][j]["x"]* self.parent.gui.pixel_scale_ratio[0],
                                         tube["bend positions"][j]["y"]* self.parent.gui.pixel_scale_ratio[1]))

                self.tube_list.append(Tube(self, tube_id=tube["tube id"], attachment_aps=[], fluid=tube["fluid"], points=points, line_width=tube["line width"]))

            elif obj_type == "Board":
                boards.append(data[i])

        self.centralWidget.controlsSidebarWidget.addBoardsToScrollWidget(boards)
        self.gui.setStatusBarMessage("Configuration opened from " + fileName)



