from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants
from overrides import overrides
from indicatorLightWidget import IndicatorLightWidget

import pyqtgraph as pg

import math
import time

"""
This file contains the class to make pyQtGraph Bearable to work with
"""


class PlotWidgetWrapper(pg.PlotWidget):
    """
    """

    def __init__(self):

        super().__init__()

        self.plot_widget = self
        self.plot_item = self.plot_widget.getPlotItem()
        self.left_view_box = self.plot_item.getViewBox()

        self.left_view_box.name = "Left"
        self.left_view_box.sigYRangeChanged.connect(self.YaxisChanged)

        self.right_view_box = None
        self.curves = {}
        self.curves_label_alias = {}

        self.left_view_box.sigResized.connect(self.updateViews)

    def setBackgroundColor(self, r:int, g:int, b:int):
        self.left_view_box.setBackgroundColor((r, g, b))

        # Fixes some bug in pyqtgraph that makes things not show
        self.plot_item.getAxis("right").setZValue(0)
        self.plot_item.getAxis("bottom").setZValue(1)
        self.plot_item.getAxis("left").setZValue(1)
        self.plot_item.getAxis("top").setZValue(1)
        self.left_view_box.setZValue(1)

    def showGrid(self, showXGrid: bool, showYGrid: bool, alpha: float = 1):
        self.plot_item.showGrid(showXGrid, showYGrid, alpha)

    def setMouseEnabled(self, xEnabled:bool, yEnabled:bool):
        self.left_view_box.setMouseEnabled(xEnabled, yEnabled)

        if self.right_view_box is not None:
            self.right_view_box.setMouseEnabled(xEnabled, yEnabled)

    def setTitleSize(self, pointSize: str):
        self.plot_item.titleLabel.setAttr("size", pointSize)

    def setTitleColor(self, color: str):
        self.plot_item.titleLabel.setAttr("color", color)

    def setClipToView(self, clip_to_view):
        self.plot_item.setClipToView(clip_to_view)

    def setAxisLabel(self, target_axis: str, label: str):
        self.plot_item.setLabel(target_axis, label)

    def setAxisLabelColor(self, target_axis: str, color: str):
        args = {"color": color}
        self.plot_item.getAxis(target_axis).setLabel(text = self.plot_item.getAxis(target_axis).labelText, units = self.plot_item.getAxis(target_axis).labelUnits, unitPrefix = self.plot_item.getAxis(target_axis).labelUnitPrefix, **args)

    def setAxisTickFont(self, target_axis: str, font):
        self.plot_item.getAxis(target_axis).setTickFont(font)

    # def setLegendLabels(self, curves, labels):
    #
    #     if self.plot_item.legend is None:
    #         self.plot_item.addLegend()
    #
    #     self.plot_item.legend.clear()
    #     for i, curve in enumerate(curves):
    #         self.plot_item.legend.addItem(curve, labels[i])

    def showLegend(self):

        if self.plot_item.legend is None:
            self.plot_item.addLegend()

        self.plot_item.legend.clear()
        for curve_label in self.curves:
            if type(self.curves[curve_label]) is not pg.InfiniteLine:
                self.plot_item.legend.addItem(self.curves[curve_label], self.curves_label_alias.get(curve_label, curve_label))

        self.plot_item.legend.setOffset((5, 5))

    def removeLegend(self):
        self.plot_item.legend.clear()

    def setLegendColors(self, backgroundRGBA: [int], borderRGBA: [int]):
        if self.plot_item.legend is None:
            self.plot_item.addLegend()

        self.plot_item.legend.setBrush(
            pg.mkBrush(backgroundRGBA[0], backgroundRGBA[1], backgroundRGBA[2], backgroundRGBA[3]))

        self.plot_item.legend.setBrush(
            pg.mkPen(borderRGBA[0], borderRGBA[1], borderRGBA[2], borderRGBA[3]))

    def setLegendFontColor(self, r:int, g:int, b:int):
        if self.plot_item.legend is None:
            self.plot_item.addLegend()

        self.plot_item.legend.setLabelTextColor((r,g,b))

    def setLegendTextSize(self, size):
        if self.plot_item.legend is None:
            self.plot_item.addLegend()

        # This is so stupid I cant with this library
        self.plot_item.legend.setLabelTextSize(str(size) + "pt")

    def addRightAxis(self):
        self.right_view_box = pg.ViewBox()
        self.right_view_box.name = "Right"

        self.right_view_box.sigYRangeChanged.connect(self.YaxisChanged)
        self.plot_item.showAxis("right")
        self.setAxisLabel("right", " ")
        self.plot_item.scene().addItem(self.right_view_box)
        self.plot_item.getAxis('right').linkToView(self.right_view_box)
        self.right_view_box.setZValue(0)
        self.right_view_box.setMouseEnabled(False, False)

        self.right_view_box.setGeometry(self.left_view_box.sceneBoundingRect())
        self.right_view_box.linkedViewChanged(self.left_view_box, self.right_view_box.XAxis)

    def hideRightAxis(self):

        # TODO: Makee sure that the signal was disconnected when deleted
        #self.right_view_box.sigYRangeChanged.disco

        self.setAxisLabel("right", "")
        self.plot_item.hideAxis("right")
        self.plot_item.scene().removeItem(self.right_view_box)
        self.plot_item.getAxis("right").unlinkFromView()

        self.right_view_box.deleteLater()
        del self.right_view_box

        self.right_view_box = None

    def addCurve(self, label: str, color: QColor, width: int = 8, axis: str = "left"):
        self.curves[label] = pg.PlotCurveItem()

        self.curves[label].setPen(pg.mkPen(color, width = width))

        if axis == "left":
            self.plot_item.addItem(self.curves[label])
        elif axis == "right":
            self.right_view_box.addItem(self.curves[label])

        return self.curves[label]

    def addInfiniteLineCurve(self, label: str, color:QColor , val, angle, width:int = 4, axis: str = "left"):
        self.curves[label] = pg.InfiniteLine(pos=val, angle=angle)

        self.curves[label].setPen(pg.mkPen(color, width = width))

        if axis == "left":
            self.plot_item.addItem(self.curves[label])
        elif axis == "right":
            self.right_view_box.addItem(self.curves[label])

        return self.curves[label]

    def addCurveLabelAlias(self, curve_label:str, alias: str):

        if curve_label in self.curves:
            self.curves_label_alias[curve_label] = alias
        else:
            print("Curve label not found! Alias not set")

    def updateViews(self):
        if self.right_view_box is not None:
            self.right_view_box.setGeometry(self.left_view_box.sceneBoundingRect())
            self.right_view_box.linkedViewChanged(self.left_view_box, self.right_view_box.XAxis)

    def clearLegend(self):
        self.plot_item.legend.clear()

    def removeAllCurves(self):

        for child in self.left_view_box.allChildren():
            if type(child) == pg.PlotCurveItem or type(child) == pg.InfiniteLine:
                self.left_view_box.removeItem(child)

        if self.right_view_box is not None:
            for child in self.right_view_box.allChildren():
                if type(child) == pg.PlotCurveItem or type(child) == pg.InfiniteLine:
                    self.right_view_box.removeItem(child)

        self.clearLegend()
        self.curves = {}
        self.curves_label_alias = {}

    @pyqtSlot(object, object)
    def YaxisChanged(self, viewbox, bounds):
        #print("Called")
        # print(a.name)
        # print(b[1])
        # print(a.state['viewRange'][1])
        pass

    """
    I Hope it is well know that I fucking hate pyqtgraph. Hours have been spent doing the stupidest simplest shit. Down
    here shall lie tons of comments on randoms things that seems helpful to do that can be implemented at a later date
    """

    """
    prevent scrolling
    """
    #self.right_view_box.installEventFilter(self)

    # def eventFilter(self, watched, event):
    #     if event.type() == QEvent.GraphicsSceneWheel:
    #         return True
    #     return super().eventFilter(watched, event)

    """
    Add event action to right click menu
    """
    # self.testAct = QAction("Test", self.plot2.left_view_box.menu)
    # self.testAct.triggered.connect(self.pleaseWorkOmg)
    # self.plot2.left_view_box.menu.addAction(self.testAct)

    """
    Add in button on plot window
    """
    # button2 = pg.ButtonItem(imageFile=pg.icons.getGraphPixmap('auto'), width= 14, parentItem=self.plot2.plot_item, pixmap=None)

    """
    How to add a curve properly
    """

    #curve = pg.PlotCurveItem()
    # self.left.addItem(curve)
    # curve.setData(x = np.array([0, 1]), y = np.array([10, 20]))
    # curve.setPen(
    #     pg.mkPen(color='r',width = 2))
    #
    # curve2 = pg.PlotCurveItem()
    # #self.left.addItem(curve)
    # curve2.setData(x=np.array([0, 1]), y=np.array([10, 35]))
    # curve2.setPen(
    #     pg.mkPen(color='r', width=2))
    # #self.left.legend.addItem(curve, 'teset')
    #
    # self.plot2.addCurve("Garbage")
    # self.plot2.addCurveLabelAlias("Garbage", "Yo Boss")
    # self.plot2.curves["Garbage"].setData(x = np.array([0, 1]), y = np.array([0, 15]))
    # self.plot2.curves["Garbage"].setPen(pg.mkPen(color=QtGui.QColor(self.colors[0].color()),width = 2))
    # #self.plot2.right_view_box.addItem(curve)
    # #self.plot2.right_view_box.addItem(curve2)