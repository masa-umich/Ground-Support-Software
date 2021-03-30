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

    def __init__(self, widget_parent, gui, is_vertical: bool = False, rows: int = 1, font_size: float = 12,
                 text: str = "Name"):
        super().__init__(widget_parent)
        self.widget = widget_parent
        self.gui = gui
        self.is_vertical = is_vertical
        self.rows = rows
        self.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.setStyleSheet("color: white")
        self.setWordWrap(True)
        self.setFont_()
        self.setFontSize(font_size)
        self.setText(text)

        if self.widget is not None:
            self.show()

    @overrides
    def setText(self, p_str, updateSize:bool = True):
        """
        Overrides the default function to provide some more functionality
        :param p_str: string to set text to
        :param updateSize: should the size of string be updated
        """
        super().setText(p_str)
        # Update the label size and make sure it is still centered
        if updateSize:
            self.setFixedSize_()

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

    def getFontSize(self):
        """
        Returns the size current font size
        """
        return self.font().pointSizeF()/self.gui.font_scale_ratio

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