from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants
from overrides import overrides


class IndicatorLightWidget(QWidget):
    """
    Small class to define an indicator light, essentially a colored circle with some text below that can display
    different colors to display status
    """

    def __init__(self, parent, labelText: str, circleRadius: int, indicatorColor: str, fontSize: int = 14,
                 Wbuffer: int = 0, Hbuffer: int = 0, LBuffer: int = 0):
        """
        Initialize the widget
        :param parent: parent of this widget, is the missionWidget
        :param labelText: the text that will be displayed under the indicator light
        :param circleRadius: the radius of the indicator circle
        :param indicatorColor: the indicator color
        :param fontSize: the font size of the indicator label
        :param Wbuffer: width buffer on the circle, pixels buffer on one side
        :param Hbuffer: height buffer on the top of the circle, pixels buffer on one side
        :param LBuffer: height buffer between the label and the circle
        """
        super().__init__(parent)

        # Basic setup
        self.missionWidget = parent
        self.gui = self.missionWidget.gui
        self.labelText = labelText
        self.circle_radius = circleRadius * self.gui.pixel_scale_ratio[0]
        self.fontSize = fontSize
        self.wBuffer = Wbuffer * self.gui.pixel_scale_ratio[0]
        self.hBuffer = Hbuffer * self.gui.pixel_scale_ratio[1]
        self.lBuffer = LBuffer * self.gui.pixel_scale_ratio[1]
        # Painter controls the drawing of everything on the widget
        self.painter = QPainter()
        self.indicatorColor = indicatorColor

        # Define the font for the widget
        monospace_light_font = QFont()
        monospace_light_font.setStyleStrategy(QFont.PreferAntialias)
        monospace_light_font.setFamily(Constants.monospace_font)
        monospace_light_font.setWeight(QFont.Light)

        # Declare the label and set it parameters
        self.label = QLabel(self)
        monospace_light_font.setPointSize(self.fontSize * self.gui.font_scale_ratio)
        self.label.setFont(monospace_light_font)
        self.label.setStyleSheet("color: white")
        self.label.setText(self.labelText)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label.adjustSize()
        self.label.setFixedHeight(self.label.fontMetrics().boundingRect(self.label.text()).height())
        self.label.show()

        # Resize the widget to fit exactly the circle and the label
        self.resize(self.circle_radius*2 + 2*self.wBuffer, self.circle_radius*2 + self.hBuffer + self.label.height() + self.lBuffer)

        # Move the label to be centered on the circle
        self.label.move(self.circle_radius + self.wBuffer - self.label.width()/2, self.circle_radius*2 + self.hBuffer + self.lBuffer)
        self.show()

    def setIndicatorColor(self, color: str):
        """
        Set the Indicator color for the widget
        :param color: Color as string, Green, Yellow, or Red
        """
        self.indicatorColor = color

    #@overrides
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
        pen.setWidth(Constants.line_width/2)
        pen.setColor(Constants.MASA_Beige_color)
        self.painter.setPen(pen)

        # Set the brush color to the indicator color
        if self.indicatorColor == "Green":
            self.painter.setBrush(QBrush(Constants.Indicator_Green_color, Qt.SolidPattern))
        elif self.indicatorColor == "Yellow":
            self.painter.setBrush(QBrush(Constants.Indicator_Yellow_color, Qt.SolidPattern))
        elif self.indicatorColor == "Red":
            self.painter.setBrush(QBrush(Constants.Indicator_Red_color, Qt.SolidPattern))
        else:
            self.painter.setBrush(Qt.NoBrush)

        # Draw the ellipse with a beige border, buffers on width and height
        self.painter.drawEllipse(QPoint(self.circle_radius + self.wBuffer, self.circle_radius + self.hBuffer),
                                 self.circle_radius, self.circle_radius)
        self.painter.setBrush(Qt.NoBrush)

        self.painter.end()
