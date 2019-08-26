from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from constants import Constants


class Tube:

    object_name = "Tube"

    def __init__(self, parent: QWidget, start_pos: QPoint, end_pos: QPoint, fluid: int):

        self.parent = parent
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.fluid = fluid

    def setStartPos(self, start_pos):
        self.start_pos = start_pos

    def setEndPos(self, end_pos):
        #self.end_pos = end_pos

        diff = self.start_pos - end_pos

        if abs(diff.x()) > abs(diff.y()):
            self.end_pos = QPoint(end_pos.x(), self.start_pos.y())
        else:
            self.end_pos = QPoint(self.start_pos.x(), end_pos.y())



    def draw(self):
        self.parent.painter.setPen(Constants.fluidColor[self.fluid])
        self.parent.painter.drawLine(self.start_pos, self.end_pos)