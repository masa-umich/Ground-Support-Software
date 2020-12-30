from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from overrides import overrides


class ObjectButton(QPushButton):
    """
    Button class that holds a data file
    """

    # Allowed data types, including solenoid state (0 or 1)
    allowed_data_types = ['Force','Temperature','Pressure','State']
    def __init__(self, name, object_, dataFile, dataType, parent=None):
        """
        Init for ObjectButton

        :param name: name on button
        :param object_: object button is assigned to
        :param dataFile: data file tied to button
        :param dataType: type of data in [Force, Temperature, Pressure, State]
        :param parent: parent window
        """
        super().__init__(name,parent)
        self.parent = parent
        self.name = name
        self.object_ = object_
        self.dataFile = dataFile
        self.dataType = dataType

        # Make sure button has no label
        self.setText("")

        # No background/ border and allow for custom right click options
        self.setStyleSheet("background-color:transparent;border:0;")
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        self.setToolTip("SN: " + self.object_.serial_number)

        self.resize(self.object_.width, self.object_.height)
        self.move(self.object_.position.x(), self.object_.position.y())

        # HMM: I feel strange about the fact the button is connecting to inside the object class
        # Connect click action to onClick function inside object class
        self.clicked.connect(lambda: self.object_.onClick())

        self.show()
        # Raise button above label
        self.raise_()

        assert dataType in self.allowed_data_types

    @overrides
    def mousePressEvent(self, event: QMouseEvent):
        """
        Called when mouse is pressed on a button. Used for drag and drop of objects

        :param event: variable holding event data
        """

        # If left click and the button is currently being edited
        if event.button() == Qt.LeftButton & self.object_.is_being_edited:
            # Set drag start position
            self.drag_start_pos = event.pos()

        super().mousePressEvent(event)

    @overrides
    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Called when mouse is moving a button. Used for drag and drop of objects

        :param event: variable holding event data
        """

        # For some unknown reason mouse move events handle buttons differently on OSX and Windows
        target_button = Qt.LeftButton
        if self.parent.gui.platform == "Windows":
            target_button = Qt.NoButton
        # Only drag if the right button is pressed, the object is being edited, and position is not locked
        if event.button() == target_button and self.object_.is_being_edited and not self.object_.position_locked:
            # I have no idea where the 22 comes from
            # 22 is for non full screen on my (all?) macs
            # HMM: Elegant Solution?
            self.window_pos = self.parent.parent.pos() #+ QPoint(0, 22)

            # Sets that the object is currently being moved
            self.object_.is_being_dragged = True

            # Move the button into place on screen
            pos = event.globalPos() - self.window_pos - self.drag_start_pos

            # Checks if the object should be snapped into place, and get that new pos if it does
            pos = self.object_.checkApAlignment(pos)

            # Moves the object into its new position
            self.object_.move(pos)

        super().mouseMoveEvent(event)

    @overrides
    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Called when mouse releases a button. Used for drag and drop of objects

        :param event: variable holding event data
        """

        # Checks if the object is currently being dragged
        if event.button() == Qt.LeftButton and self.object_.is_being_edited and self.object_.is_being_dragged:
            # Does background stuff when object is released
            super().mouseReleaseEvent(event)

            # Makes sure that the button is still checked as editing and edit panel does not disappear
            self.parent.controlsPanel.addEditingObject(self.object_)
            self.object_.is_being_dragged = False
        else:
            super().mouseReleaseEvent(event)




