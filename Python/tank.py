from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import time
from overrides import overrides

from constants import Constants
from MathHelper import MathHelper
from avionicsObject import AvionicsObject
from datetime import datetime
from LedIndicatorWidget import LedIndicator


"""
Class to handle all tank objects and their functionality 
"""


class Tank(AvionicsObject):

    object_name = "Tank"

    def __init__(self, widget_parent: QWidget, position: QPointF, fluid: int, width: float = 88*1,
                 height: float = 170*1, name: str = "Tank",
                 scale: float = 1, serial_number: str = '',
                 long_name: str = 'Tank', is_vertical: bool = True,
                 locked: bool = False, position_locked: bool = False, _id: int = None,
                 serial_number_label_pos: str = "Bottom", serial_number_label_local_pos: QPointF = QPointF(0, 0),
                 serial_number_label_font_size: float = 10, long_name_label_pos: str = "Top",
                 long_name_label_local_pos: QPointF = QPointF(0 , 0), long_name_label_font_size: float = 12,
                 long_name_label_rows: int = 1, long_name_visible:bool = True, serial_number_visible:bool = True,
                 channel: str = 'Undefined', board: str = 'Undefined'):
        """
        Initializer for Solenoid

        :param widget_parent: parent widget
        :param position: position of icon on screen
        :param fluid: fluid in object
        :param width: width of object
        :param height: height of object
        :param name: name of object
        :param scale: scale applied to the object
        :param serial_number: abbreviated name on schematics
        :param long_name: human-readable name for display on screen
        :param is_vertical: tracker if object is drawn vertically
        :param locked: tracker if the object is locked from editing
        :param position_locked: tracker if the object position is locked
        :param _id: unique internal gui id of the object
        :param serial_number_label_pos: string of where the serial number label is
        :param serial_number_label_local_pos: local position on where serial number label is
        :param serial_number_label_font_size: font size of serial number label
        :param long_name_label_pos: string of where the long name label is
        :param long_name_label_local_pos: local position on where long name label is
        :param long_name_label_font_size: font size of long name label
        :param long_name_label_rows: how many rows long name label should have
        """

        ## Initialize underlying class
        super().__init__(parent=widget_parent, position=position, fluid=fluid, width=width, height=height,
                         name=name, is_vertical=is_vertical, scale=scale,
                         serial_number=serial_number, long_name=long_name, locked=locked, position_locked=position_locked,
                         _id=_id, serial_number_label_pos=serial_number_label_pos,
                         serial_number_label_local_pos=serial_number_label_local_pos,
                         serial_number_label_font_size=serial_number_label_font_size,
                         long_name_label_pos=long_name_label_pos, long_name_label_local_pos=long_name_label_local_pos,
                         long_name_label_font_size=long_name_label_font_size,
                         long_name_label_rows=long_name_label_rows,long_name_visible=long_name_visible,
                         serial_number_visible=serial_number_visible, board=board, channel=channel)

        self.window = self.widget_parent.window

        # Tracks the percentage of fluid in the tank
        self.fillPercent = 0
        self.pressureSetPoint = None
        self.pressureLowerBounds = None
        self.pressureUpperBounds = None

        self.updateToolTip()

        self.runContextMenuItems.append("Set Pressure Config")
        self.run_context_menu.addAction("Set Pressure Config")

        #self.long_name_label.setStyleSheet("background-color:" + Constants.MASA_Blue_color.name() + "; border: none")

        self.gui.liveDataHandler.dataPacketSignal.connect(self.updateFromDataPacket)

    @overrides
    def onClick(self):
        """
        When a tank is clicked this function is called
        This is really only useful for adding plots and
        selecting the tank for editing
        """
        super().onClick()

        if not self.widget_parent.parent.is_editing and self.gui.debug_mode:
            # This is for testing and will normally be used with capacitive level sensor
            self.fillPercent += .05

        # Tells widget painter to update screen
        self.widget_parent.update()
        self.updateToolTip()

    def updateValues(self, setPoint, lowerBound, upperBound):
        """
        Updates the tank values
        :param setPoint: Pressure set point
        :param lowerBound: lower % bound
        :param upperBound: upper % bound
        """

        self.pressureSetPoint = setPoint
        self.pressureLowerBounds = lowerBound
        self.pressureUpperBounds = upperBound

        self.updateToolTip()

    @overrides
    def draw(self):
        """
        Draws the tank icon on screen
        """
        # Height of curved arc at top and bottom of tank
        arcHeight = 20 * self.scale * self.widget_parent.gui.pixel_scale_ratio[0]

        # Draws the tank outline
        path = QPainterPath()
        if self.is_vertical:
            path.moveTo(0,arcHeight)
            path.arcTo(QRectF(0, 0, self.width, arcHeight * 2), 180, -180)
            path.lineTo(self.width, self.height - 2 * arcHeight) 
            path.arcTo(QRectF(self.width, path.currentPosition().y(), - self.width, arcHeight * 2), 180, 180)
            path.lineTo(0, arcHeight)
        else:
            path.moveTo(arcHeight,0)
            path.arcTo(QRectF(0, 0,  arcHeight * 2, self.height), 90, 180) 
            path.lineTo(self.width - arcHeight, self.height) 
            path.arcTo(path.currentPosition().x()-arcHeight, 0 ,arcHeight*2,self.height, -90, 180)
            path.lineTo(arcHeight, 0)
            
        path.translate(self.position.x(), self.position.y()) # Translate it into position
        self.widget_parent.painter.drawPath(path) # Draw Path

        # Debug randomness
        #self.widget_parent.painter.fillRect(QRectF(self.position.x(), self.position.y(), 10, 10), Constants.fluidColor[self.fluid])

        # End tank outline draw

        # TODO: Make this a bit more basic to understand / helper function for filling an arc
        # Fill in bottom arc
        path = QPainterPath()
        self.widget_parent.painter.setPen(Constants.fluidColor[self.fluid])
        self.widget_parent.painter.setBrush(Constants.fluidColor[self.fluid])

        # Maps the fill percentage of the tank to an angle to fill the bottom arc
        bottomArcFillAngle = MathHelper.mapValue(self.fillPercent, 0, arcHeight / self.height, 0, 90)

        path.moveTo(self.position.x() + self.width / 2, self.position.y() + self.height)
        path.arcTo(QRectF(self.position.x(), self.position.y() + self.height - 2 * arcHeight, self.width, arcHeight * 2), 270, bottomArcFillAngle)
        path.lineTo(self.position.x() + self.width / 2, path.currentPosition().y())
        path.lineTo(self.position.x() + self.width / 2, self.position.y() + self.height)

        path.moveTo(self.position.x() + self.width / 2, self.position.y() + self.height)
        path.arcTo(QRectF(self.position.x(), self.position.y() + self.height - 2 * arcHeight, self.width, 2 * arcHeight), 270,
                   -bottomArcFillAngle)
        path.lineTo(self.position.x() + self.width / 2, path.currentPosition().y())
        path.lineTo(self.position.x() + self.width / 2, self.position.y() + self.height)

        self.widget_parent.painter.drawPath(path)
        # End fill in bottom arc

        # Fill in tank body
        # Maps fill percentage to the height of the body to fill
        bodyFillHeight = MathHelper.mapValue(self.fillPercent, arcHeight / self.height, 1 - arcHeight / self.height, 0,
                                       self.height - 2 * arcHeight +1)

        self.widget_parent.painter.fillRect(QRectF(self.position.x(), self.position.y() - arcHeight + self.height - bodyFillHeight, self.width, bodyFillHeight), Constants.fluidColor[self.fluid])
        # End fill in tank body

        # Fill in top arc
        path = QPainterPath()
        self.widget_parent.painter.setPen(Constants.fluidColor[self.fluid])
        self.widget_parent.painter.setBrush(Constants.fluidColor[self.fluid])

        topArcFillAngle = MathHelper.mapValue(self.fillPercent, 1 - (arcHeight / self.height), 1, 0, 90)

        path.moveTo(self.position.x() + self.width, self.position.y() + arcHeight)
        path.arcTo(QRectF(self.position.x(), self.position.y(), self.width, arcHeight * 2), 0, topArcFillAngle)
        if topArcFillAngle > 0:
            path.lineTo(self.position.x() + self.width / 2, path.currentPosition().y())
            path.lineTo(self.position.x() + self.width / 2, self.position.y() + arcHeight)

        path.moveTo(self.position.x(), self.position.y() + arcHeight)
        path.arcTo(QRectF(self.position.x(), self.position.y(), self.width, arcHeight * 2), 180, -topArcFillAngle)
        if topArcFillAngle > 0:
            path.lineTo(self.position.x() + self.width / 2, path.currentPosition().y())
            path.lineTo(self.position.x() + self.width / 2, self.position.y() + arcHeight)

        self.widget_parent.painter.drawPath(path)

        # self.widget_parent.painter.eraseRect(
        #     QRect(self.long_name_label.pos().x(), self.long_name_label.pos().y(), self.long_name_label.width(),
        #           self.long_name_label.height()))

        self.widget_parent.painter.setBrush(0)
        # End fill in top arc

        super().draw()

    def updateToolTip(self):
        """
        Called to update the tooltip of the tank
        """

        text = ""

        if self.isAvionicsFullyDefined():
            text += "Channel: %s\n" % (self.getBoardChannelString())
        else:
            text += "Channel:\n"

        text += "Fill Level: " + str(int(self.fillPercent * 100)) + "%"

        if self.pressureSetPoint is not None:
            text += "\n"
            text += "Set Pressure: " + str(self.pressureSetPoint) + "psi\n"
            text += "Lower Pressure Bound: " + str(self.pressureLowerBounds) + "psi\n"
            text += "Upper Pressure Bound: " + str(self.pressureUpperBounds) + "psi"

        self.setToolTip_(text)

    @overrides
    def contextMenuEvent_(self, event):

        action = super().contextMenuEvent_(event)

        if action is not None:
            if action.text() == "Set Pressure Config":
                self.showSetPresConfigDialog()

    def showSetPresConfigDialog(self):
        """
        Shows a dialog when the tank context menu is clicked. Allows the user to update the pressure set point,
        lower and upper bounds
        """

        # Create the dialog
        dialog = QDialog(self.window)
        dialog.setWindowTitle("Set Pressure Config")
        dialog.setWindowModality(Qt.ApplicationModal)

        # Set dialog size and place in middle of window
        dialog.resize(450 * self.gui.pixel_scale_ratio[0], 240 * self.gui.pixel_scale_ratio[1])
        dialog.setMinimumWidth(450 * self.gui.pixel_scale_ratio[0])
        dialog.setMinimumWidth(240 * self.gui.pixel_scale_ratio[1])
        dialog.move((self.window.width() - dialog.width()) / 2,
                    (self.window.height() - dialog.height()) / 2)

        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.default_font)
        font.setPointSize(14 * self.gui.font_scale_ratio)

        # Vertical layout to hold everything
        verticalLayout = QVBoxLayout(dialog)

        # enable box
        enable_layout = QHBoxLayout()
        enable_button = QPushButton("Enable Press")
        enable_button.setFont(font)
        enable_button.setDefault(False)
        enable_button.setAutoDefault(False)
        enable_button.clicked.connect(lambda: self.setTankStatus(1))
        disable_button = QPushButton("Disable Press")
        disable_button.setFont(font)
        disable_button.setDefault(False)
        disable_button.setAutoDefault(False)
        disable_button.clicked.connect(lambda: self.setTankStatus(0))
        enable_layout.addWidget(enable_button)
        enable_layout.addWidget(disable_button)
        verticalLayout.addLayout(enable_layout)

        # Create the form layout that will hold the text box
        formLayout = QFormLayout()
        formLayout.setFieldGrowthPolicy(
            QFormLayout.AllNonFixedFieldsGrow)  # This is properly resize textbox on OSX
        verticalLayout.addLayout(formLayout)

        # Create spin boxes
        setPointBox = QDoubleSpinBox()
        setPointBox.setDecimals(1)
        setPointBox.setMinimum(0)
        setPointBox.setMaximum(1001)
        setPointBox.setValue(0) if self.pressureSetPoint is None else setPointBox.setValue(self.pressureSetPoint)
        setPointBox.setSuffix("psi")
        setPointBox.setFont(font)

        lowBoundBox = QDoubleSpinBox()
        lowBoundBox.setMaximum(1001)
        lowBoundBox.setMinimum(0)
        lowBoundBox.setValue(0) if self.pressureLowerBounds is None else lowBoundBox.setValue(self.pressureLowerBounds)
        lowBoundBox.setSuffix("psi")
        lowBoundBox.setDecimals(1)
        lowBoundBox.setFont(font)
        
        highBoundBox = QDoubleSpinBox()
        highBoundBox.setMaximum(1001)
        highBoundBox.setMinimum(0)
        highBoundBox.setValue(0) if self.pressureUpperBounds is None else highBoundBox.setValue(self.pressureUpperBounds)
        highBoundBox.setSuffix("psi")
        highBoundBox.setDecimals(1)
        highBoundBox.setFont(font)

        spinBoxes = [setPointBox, lowBoundBox, highBoundBox]

        label1 = QLabel("Pressure Set Point:")
        label1.setFont(font)
        label2 = QLabel("Lower Bound:")
        label2.setFont(font)
        label3 = QLabel("Upper Bound:")
        label3.setFont(font)

        # Add to the layout
        formLayout.addRow(label1, setPointBox)
        formLayout.addRow(label2, lowBoundBox)
        formLayout.addRow(label3, highBoundBox)

        # Horizontal button layout
        buttonLayout = QHBoxLayout()
        # Create the buttons, make sure there is no default option, and connect to functions
        cancel_button = QPushButton("Cancel")
        cancel_button.setFont(font)
        cancel_button.setDefault(False)
        cancel_button.setAutoDefault(False)
        cancel_button.clicked.connect(lambda: dialog.done(1))
        cancel_button.setFixedWidth(
            125 * self.gui.pixel_scale_ratio[0])  # Lazy way to make buttons not full width

        save_button = QPushButton("Save")
        save_button.setFont(font)
        save_button.setDefault(False)
        save_button.setAutoDefault(False)
        save_button.clicked.connect(lambda: self.tankDialogSave(spinBoxes, dialog))
        save_button.setFixedWidth(125 * self.gui.pixel_scale_ratio[0])

        buttonLayout.addWidget(cancel_button)
        buttonLayout.addWidget(save_button)

        verticalLayout.addLayout(buttonLayout)

        dialog.show()

    def tankDialogSave(self, spinBoxes, dialog):
        """
        Saves the new motor values and sends the commands to the board
        :param spinBoxes: spin boxes with the values
        :param dialog: dialog with motor settings
        """
        setpoint = spinBoxes[0].value()
        lowbound = spinBoxes[1].value()
        upbound = spinBoxes[2].value()

        if self.gui.debug_mode:
            self.updateValues(setpoint,lowbound,upbound)
        else:
            if self.isAvionicsFullyDefined():
                cmd_dict = {
                    "function_name": "set_control_target_pressure",
                    "target_board_addr": self.widget_parent.window.interface.getBoardAddr(self.avionics_board),
                    "timestamp": int(datetime.now().timestamp()),
                    "args": [int(self.channel), float(setpoint)]
                }
                self.gui.liveDataHandler.sendCommand(3, cmd_dict)
                time.sleep(0.1)
                cmd_dict = {
                    "function_name": "set_low_toggle_percent",
                    "target_board_addr": self.widget_parent.window.interface.getBoardAddr(self.avionics_board),
                    "timestamp": int(datetime.now().timestamp()),
                    "args": [int(self.channel), float(lowbound/setpoint)]
                }
                self.gui.liveDataHandler.sendCommand(3, cmd_dict)
                time.sleep(0.1)
                cmd_dict = {
                    "function_name": "set_high_toggle_percent",
                    "target_board_addr": self.widget_parent.window.interface.getBoardAddr(self.avionics_board),
                    "timestamp": int(datetime.now().timestamp()),
                    "args": [int(self.channel), float(upbound/setpoint)]
                }
                self.gui.liveDataHandler.sendCommand(3, cmd_dict)
        dialog.done(2)
    
    def setTankStatus(self, status):
        """
        Saves the new motor values and sends the commands to the board
        :param spinBoxes: spin boxes with the values
        :param dialog: dialog with motor settings
        """
        if self.isAvionicsFullyDefined():
            cmd_dict = {
                "function_name": "set_presstank_status",
                "target_board_addr": self.widget_parent.window.interface.getBoardAddr(self.avionics_board),
                "timestamp": int(datetime.now().timestamp()),
                "args": [int(self.channel),int(status)]
            }
            self.gui.liveDataHandler.sendCommand(3, cmd_dict)

    @pyqtSlot(object)
    def updateFromDataPacket(self, data_packet: dict):

        if self.isAvionicsFullyDefined():
            board_prefix = self.gui.controlsWindow.interface.getPrefix(self.avionics_board)
            channel_name = board_prefix + "tnk" + str(self.channel)

            setPoint = data_packet[channel_name + ".tp"]
            lowbound = data_packet[channel_name + ".lp"]
            highBound = data_packet[channel_name + ".hp"]
            self.updateValues(setPoint, lowbound, highBound)