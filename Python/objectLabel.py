from PyQt5.QtGui import *
from PyQt5.QtCore import *

from overrides import overrides
from customLabel import CustomLabel

"""
Provides custom functionality for labels specific to objects
"""

# TODO: Somehow make it that you just create and pass in a custom label but too lazy to do that now
class ObjectLabel(CustomLabel):

    def __init__(self, widget_parent, gui, object_, position_string: str = "Top", is_vertical: bool = False,
                 local_pos: QPointF = QPointF(0, 0), rows: int = 1, font_size: float = 12, text: str = "Name",
                 is_visible: bool = True):

        self.widget = widget_parent
        self.gui = gui
        self.object_ = object_
        self.is_vertical = is_vertical
        self.position_string = position_string
        self.local_pos = local_pos
        # Have to scale it, not sure if this is best location
        self.local_pos.setX(self.local_pos.x() * self.gui.pixel_scale_ratio[0])
        self.local_pos.setY(self.local_pos.y() * self.gui.pixel_scale_ratio[1])

        # Need to init values before you call super
        super().__init__(widget_parent, gui)

        self.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.setStyleSheet("color: white")
        self.setWordWrap(True)
        self.setFont_()
        self.setFontSize(font_size)
        self.setText(text)
        self.setRows(rows)
        self.show()

        self.setVisible(is_visible)

    @overrides
    def setText(self, p_str):
        """
        Overrides the default function to provide some more functionality
        :param p_str: string to set text to
        """

        # Update the label size and make sure it is still centered
        super().setText(p_str)
        self.moveToPosition()

    @overrides
    def setFontSize(self, size: int):
        """
        Updates the size of the font
        :param size: point size of the font
        """
        super().setFontSize(size)
        self.moveToPosition()

    def setRows(self, rows: int):
        """
        Sets the number of rows the label has
        :param rows: number of rows
        """

        super().setRows(rows)
        self.moveToPosition()

    # TODO: Add assert for the string positions
    # HMM: Should these positions be defined completely relative to the object location instead of global?
    def moveToPosition(self, position_string: str = None):
        """
        Sets position string ang moves label to a position relative to its object.
        Can pass in option arg to set new value to position_string, otherwise will set
        position based on last set value
        :param position_string: string representing position of label. Can be "Top", "Bottom", "Right", "Left"
        """

        if position_string is not None:
            self.position_string = position_string

        if self.position_string == "Top":
            self.move(self.getXCenterPosition(), self.object_.position.y() - self.height() - 3) # 3 is for better seperation
        elif self.position_string == "Bottom":
            self.move(self.getXCenterPosition(), self.object_.position.y() + self.object_.height + 3) # 3 is for better seperation
        elif self.position_string == "Right":
            self.move(self.object_.position.x() + self.object_.width + 3, self.getYCenterPosition())
        elif self.position_string == "Left":
            self.move(self.object_.position.x() - self.width() - 3, self.getYCenterPosition())
        elif self.position_string == "Custom":
            self.move(self.object_.position.x() + self.local_pos.x(), self.object_.position.y() + self.local_pos.y())

        self.setLocalPosition()

    def getXCenterPosition(self):
        """
        Gets what x position the label needs to be placed at to be centered on its base object
        """
        return self.object_.position.x() + (self.object_.width / 2) - (self.width() / 2)

    def getYCenterPosition(self):
        """
        Gets what y position the label needs to be placed at to be centered on its base object
        """
        # Not sure why the -2 is needed but may have to due with extra space above text
        return self.object_.position.y() + (self.object_.height / 2) - (self.height() / 2) - 2

    def setLocalPosition(self):
        """
        Sets the local position aka where the label is relative to the (0,0) of the object
        """
        self.local_pos = self.pos() - self.object_.position


    # @overrides
    # def paintEvent(self, event):
    #     """
    #     Overrides the default painter to enable painting the text vertically
    #
    #     :param event: event passed along
    #     """
    #     rotation = 90
    #     painter = QPainter(self)
    #     painter.setPen(Qt.white)
    #     painter.rotate(rotation * self.is_vertical)
    #     if self.text:
    #         if self.is_vertical:
    #             painter.drawText(QPointF(0,0), self.text())
    #         else:
    #             self.show()
    #             painter.drawText(QPointF(0, self.fontMetrics().boundingRect(self.text()).height()), self.text())
    #     painter.end()

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
            self.position_string = "Custom"
            self.widget.controlsPanel.updateEditPanelFields(self.object_)
            self.setFixedSize_()  # For some reason it glitches to be smaller so this is to prevent this

        super().mousePressEvent(event)

    @overrides
    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Called when mouse is moving a button. Used for drag and drop of objects/ labels

        :param event: variable holding event data
        """

        # For some unknown reason mouse move events handle buttons differently on OSX and Windows
        # target_button = Qt.LeftButton
        # if self.widget.gui.platform == "Windows":
        target_button = Qt.NoButton

        if event.button() == target_button and self.object_.is_being_edited:

            # If the gui is in full screen on mac don't apply the extra offset
            if self.gui.platform == "OSX" and self.gui.controlsWindow.isFullScreen():
                window_pos = self.gui.controlsWindow.window.pos()
            elif self.gui.platform == "Windows" and self.gui.controlsWindow.isFullScreen():
                window_pos = self.gui.controlsWindow.pos() + self.gui.controlsWindow.central_widget_offset - self.gui.controlsWindow.central_widget.pos()
            else:
                window_pos = self.gui.controlsWindow.pos() + self.gui.controlsWindow.central_widget_offset

            # Move the button into place on screen
            pos = event.globalPos() - window_pos - self.drag_start_pos

            # Moves the object into its new position
            self.move(pos)

            # Updates the new local position
            # HMM: May want to move this call to an overridden move() function
            self.setLocalPosition()

        super().mouseMoveEvent(event)

    @overrides
    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Called when mouse releases a button. Used for drag and drop of objects/labels

        :param event: variable holding event data
        """

        # Checks if the label is currently being dragged
        if event.button() == Qt.LeftButton and self.object_.is_being_edited and self.object_.is_being_dragged:
            # Does background stuff when object is released
            super().mouseReleaseEvent(event)

            # Makes sure that the button is still checked as editing and edit panel does not disappear
            self.widget.controlsPanel.addEditingObject(self.object_)
        else:
            super().mouseReleaseEvent(event)

    def generateSaveDict(self):
        save_dict = {
            "pos string": self.position_string,
            "local pos": {"x": self.local_pos.x()/self.gui.pixel_scale_ratio[0], "y": self.local_pos.y()/self.gui.pixel_scale_ratio[1]},
            "rows": self.rows,
            "font size": self.getFontSize(),
            "is visible": self.isVisible()
        }
        return save_dict