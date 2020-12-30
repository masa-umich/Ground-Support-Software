from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from overrides import overrides
from constants import Constants

"""
Provides custom functionality for labels
"""


# TODO: Add alignment lines to these too HMM: Is that really worth it though
class CustomLabel(QLabel):

    def __init__(self, widget_parent, object_, position_string: str = "Top", is_vertical: bool = False,
                 local_pos: QPoint = QPoint(0, 0), rows: int = 1, font_size: float = 12, text: str = "Name"):
        super().__init__(widget_parent)
        self.widget = widget_parent
        self.gui = self.widget.gui
        self.object_ = object_
        self.is_vertical = is_vertical
        self.position_string = position_string
        self.local_pos = local_pos
        self.rows = rows
        self.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.setStyleSheet("color: white")
        self.setWordWrap(True)
        self.setFont_()
        self.setFontSize(font_size)
        self.setText(text)
        self.show()

    @overrides
    def setText(self, p_str):
        """
        Overrides the default function to provide some more functionality
        :param p_str: string to set text to
        """
        super().setText(p_str)
        # Update the label size and make sure it is still centered
        self.setFixedSize_()
        self.moveToPosition()

    def setFont_(self, font: QFont = None):

        if font is not None:
            self.setFont(font)
        else:
            font = QFont()
            font.setStyleStrategy(QFont.PreferAntialias)
            font.setFamily(Constants.default_font)
            self.setFont(font)

    def setFontSize(self, size: int):
        """
        Updates the size of the font
        :param size: point size of the font
        """
        font = self.font()
        font.setPointSizeF(size * self.gui.font_scale_ratio)
        self.setFont(font)
        # Update the label size and make sure it is still centered
        self.setFixedSize_()
        self.moveToPosition()

    def setFixedSize_(self):
        """
        Sets the label size to be exactly the size of the text
        """

        # Get the height of a line of text and the width of the text
        fixedHeight = self.fontMetrics().boundingRect(self.text()).height()
        textWidth = self.fontMetrics().boundingRect(self.text()).width()

        # Find the longest word
        maxWordWidth = 0
        for word in self.text().split():
            wordWidth = self.fontMetrics().boundingRect(word).width()
            if wordWidth > maxWordWidth:
                maxWordWidth = wordWidth

        # See if any one word is longer than the fixed width
        fixedWidth = textWidth/self.rows
        if fixedWidth < maxWordWidth:
            fixedWidth = maxWordWidth

        # Sets the fixed size
        if self.is_vertical:
            self.setFixedSize(fixedHeight,self.width())
        else:
            self.setFixedHeight(self.rows * fixedHeight)
            if self.rows > 1:
                # TODO: Fix this +40 *blah. Currently addresses the problem that causes the last word to be clipped
                self.setFixedWidth(fixedWidth + (self.gui.pixel_scale_ratio[0]*(40 * (self.getFontSize()/23)))) # 40 is a lazy mans fix right now
            else:
                self.setFixedWidth(fixedWidth + 5)  # 5 is a small buffer

    def setIsVertical(self, is_vertical):
        """
        Sets if the label is vertical or not
        :param is_vertical: is label vertical
        """
        self.is_vertical = is_vertical
        self.setFixedSize_()

    def setRows(self, rows: int):
        """
        Sets the number of rows the label has
        :param rows: number of rows
        """
        # Prevent 0 or negative rows
        if rows < 1:
            self.rows = 1
        else:
            self.rows = rows

        # Update the label size and make sure it is still centered
        self.setFixedSize_()
        self.moveToPosition()

    def getFontSize(self):
        """
        Returns the size current font size
        """
        return self.font().pointSizeF()/self.gui.font_scale_ratio

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
            self.move(self.object_.position + self.local_pos)

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
    #             painter.drawText(QPoint(0,0), self.text())
    #         else:
    #             self.show()
    #             painter.drawText(QPoint(0, self.fontMetrics().boundingRect(self.text()).height()), self.text())
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
        target_button = Qt.LeftButton
        if self.widget.gui.platform == "Windows":
            target_button = Qt.NoButton

        if event.button() == target_button and self.object_.is_being_edited:
            # I have no idea where the 22 comes from
            # 22 is for non full screen on my (all?) macs
            # HMM: Elegant Solution?
            self.window_pos = self.widget.parent.pos() #+ QPoint(0, 22)

            # Move the button into place on screen
            pos = event.globalPos() - self.window_pos - self.drag_start_pos

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
            "local pos": {"x": self.local_pos.x(), "y": self.local_pos.y()},
            "rows": self.rows,
            "font size": self.getFontSize()
        }
        return save_dict