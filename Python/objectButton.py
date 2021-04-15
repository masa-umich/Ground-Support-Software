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
        self.central_widget = self.parent.parent
        self.window = self.central_widget.parent
        self.name = name
        self.object_ = object_
        self.dataFile = dataFile
        self.dataType = dataType
        self.drag_start_pos = None

        # Not sure why this is different, but seems to due with the fact that windows handles central widget differently
        if self.window.gui.platform == "Windows":
            self.central_widget_offset = self.central_widget.pos() - self.window.pos() + QPoint(0, self.window.menuBar().height())
        elif self.window.gui.platform == "OSX":
            self.central_widget_offset = self.window.pos()

        # Make sure button has no label
        self.setText("")

        # No background/ border and allow for custom right click options
        self.setStyleSheet(""
                           "QPushButton{background-color:transparent;border:0;}"
                           "QToolTip{background-color:black;color:white;}")
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
        self.setFocus()  # Want the button to have focus when created

        assert dataType in self.allowed_data_types

    @overrides
    def mousePressEvent(self, event: QMouseEvent):
        """
        Called when mouse is pressed on a button. Used for drag and drop of objects

        :param event: variable holding event data
        """

        # If left click and the button is currently being edited
        if event.button() == Qt.LeftButton & self.object_.doesObjectHaveFocus() & self.object_.central_widget.is_editing:
            # Set drag start position
            self.parent.controlsPanel.addEditingObject(self.object_)
            self.drag_start_pos = event.pos()

        super().mousePressEvent(event)

    @overrides
    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Called when mouse is moving a button. Used for drag and drop of objects

        :param event: variable holding event data
        """

        # If the start position does not exist, then it should not be moved so return out
        if self.drag_start_pos is None:
            return

        # Only drag if the right button is pressed, the object is being edited, and position is not locked
        if event.button() == Qt.NoButton and self.object_.is_being_edited and not self.object_.position_locked:
            # I have no idea where the 22 comes from
            # 22 is for non full screen on my (all?) macs
            # HMM: Elegant Solution?

            # If the gui is in full screen on mac don't apply the extra offset
            if self.window.gui.platform == "OSX" and self.window.isFullScreen():
                self.window_pos = self.window.pos()
            else:
                self.window_pos = self.window.pos() + self.central_widget_offset

            # Sets that the object is currently being moved
            self.object_.is_being_dragged = True

            # Move the button into place on screen
            pos = event.globalPos() - self.window_pos - self.drag_start_pos

            # Check if the shift ket is being held down, if so check if the object has x or y alignment right now
            mod = QApplication.keyboardModifiers()
            if mod == Qt.ShiftModifier:
                x_aligned = False
                y_aligned = False
                # Loop through ap and see if any are aligned currently
                for ap in self.object_.anchor_points:
                    if ap.x_aligned:
                        x_aligned = True
                    if ap.y_aligned:
                        y_aligned = True

                # If the ap is aligned, lock the X/Y position so the object can only be moved along that line, also
                # update the drag start position to prevent weird movement when the object encounters another ap
                if x_aligned and not y_aligned:
                    pos.setX(self.object_.position.x())
                    self.drag_start_pos.setX(event.pos().x())
                elif y_aligned and not x_aligned:
                    pos.setY(self.object_.position.y())
                    self.drag_start_pos.setY(event.pos().y())

            # Checks if the object should be snapped into place, and get that new pos if it does
            pos = self.object_.checkApAlignment(pos)

            # Calculate the difference in location
            dif = pos - self.object_.position

            # Move all teh editing objects that amount
            self.object_.central_widget.controlsWidget.moveObjectGroup(dif)

        super().mouseMoveEvent(event)

    @overrides
    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Called when mouse releases a button. Used for drag and drop of objects

        :param event: variable holding event data
        """

        # Checks if the object is currently being dragged
        if event.button() == Qt.LeftButton and self.object_.button.hasFocus() and self.object_.is_being_dragged:
            # Does background stuff when object is released
            super().mouseReleaseEvent(event)

            # Makes sure that the button is still checked as editing and edit panel does not disappear
            self.parent.controlsPanel.addEditingObject(self.object_)
            self.object_.is_being_dragged = False
            self.drag_start_pos = None
        else:
            super().mouseReleaseEvent(event)

    @overrides
    def keyPressEvent(self, event: QKeyEvent):
        """
        Checks for keyboard events, only occurs when an object is in focus. Currently will allow to move an object with
        the arrow keys
        :param event: passed in event
        """

        super().keyPressEvent(event)  # Not sure if super has to be called, but doing it for best practice

        # Default pixel move distance, essential the distance the object will move when an arrow key is pressed
        move_dist = 5

        # If the shift key is being held down, allow for finer moving of the object
        if event.modifiers() & Qt.ShiftModifier:  # Idk why this works
            move_dist = 1

        # Move the selected group by the move dist amount
        if event.key() == Qt.Key_Left:
            self.object_.central_widget.controlsWidget.moveObjectGroup(QPoint(-move_dist, 0))
        elif event.key() == Qt.Key_Right:
            self.object_.central_widget.controlsWidget.moveObjectGroup(QPoint(move_dist, 0))
        elif event.key() == Qt.Key_Up:
            self.object_.central_widget.controlsWidget.moveObjectGroup(QPoint(0, -move_dist))
        elif event.key() == Qt.Key_Down:
            self.object_.central_widget.controlsWidget.moveObjectGroup(QPoint(0, move_dist))

        # Idk why but calling super causes the button to lose focus, so set that back
        self.object_.button.setFocus()