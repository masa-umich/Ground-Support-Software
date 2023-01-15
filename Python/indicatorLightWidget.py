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

    def __init__(self, parent, gui, labelText: str, circleRadius: int, indicatorColor: str, fontSize: int = 14,
                 Wbuffer: int = 0, Hbuffer: int = 0, LBuffer: int = 0, darkMode:bool = False):
        """
        Initialize the widget
        :param parent: parent of this widget
        :param labelText: the text that will be displayed under the indicator light
        :param circleRadius: the radius of the indicator circle
        :param indicatorColor: the indicator color
        :param fontSize: the font size of the indicator label
        :param Wbuffer: width buffer on the circle, pixels buffer on one side
        :param Hbuffer: height buffer on the top of the circle, pixels buffer on one side
        :param LBuffer: height buffer between the label and the circle
        :param darkMode: Display outline and text as dark instead of bright
        """
        super().__init__(parent)

        # Basic setup
        self.parent = parent
        self.gui = gui
        self.labelText = labelText
        self.fontSize = fontSize
        self.darkMode = darkMode

        monospace_light_font = QFont()

        # TODO: Local bandaid to big problem
        if gui is not None:
            self.circle_radius = circleRadius * self.gui.pixel_scale_ratio[0]
            self.wBuffer = Wbuffer * self.gui.pixel_scale_ratio[0]
            self.hBuffer = Hbuffer * self.gui.pixel_scale_ratio[1]
            self.lBuffer = LBuffer * self.gui.pixel_scale_ratio[1]
            monospace_light_font.setPointSize(int(self.fontSize * self.gui.font_scale_ratio))
        else:
            self.circle_radius = circleRadius
            self.wBuffer = Wbuffer
            self.hBuffer = Hbuffer
            self.lBuffer = LBuffer
            monospace_light_font.setPointSize(self.fontSize)

        # Painter controls the drawing of everything on the widget
        self.painter = QPainter()
        self.indicatorColor = indicatorColor

        # Define the font for the widget

        monospace_light_font.setStyleStrategy(QFont.PreferAntialias)
        monospace_light_font.setFamily(Constants.monospace_font)
        monospace_light_font.setWeight(QFont.Light)
        monospace_light_font.setHintingPreference(QFont.PreferNoHinting)

        # Declare the label and set it parameters
        self.label = QLabel(self)
        self.label.setFont(monospace_light_font)
        if not darkMode:
            self.label.setStyleSheet("color: white")
        else:
            self.label.setStyleSheet("color: black")
        self.label.setText(self.labelText)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label.adjustSize()
        self.label.setFixedHeight(self.label.fontMetrics().boundingRect(self.label.text()).height())
        self.label.show()

        # Resize the widget to fit exactly the circle and the label
        self.resize(int(self.circle_radius*2 + 2*self.wBuffer), int(self.circle_radius*2 + self.hBuffer + self.label.height() + self.lBuffer))

        # Move the label to be centered on the circle
        self.label.move(int(self.circle_radius + self.wBuffer - self.label.width()/2), int(self.circle_radius*2 + self.hBuffer + self.lBuffer))
        self.show()

    def setIndicatorColor(self, color: str):
        """
        Set the Indicator color for the widget
        :param color: Color as string, Green, Yellow, or Red
        """
        self.indicatorColor = color

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
        pen.setWidth(int(Constants.line_width/2))
        if not self.darkMode:
            pen.setColor(Constants.MASA_Beige_color)
        else:
            pen.setColor(QColor(44, 44, 44))
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
        self.painter.drawEllipse(QPointF(self.circle_radius + self.wBuffer, self.circle_radius + self.hBuffer),
                                 self.circle_radius, self.circle_radius)
        self.painter.setBrush(Qt.NoBrush)

        self.painter.end()
