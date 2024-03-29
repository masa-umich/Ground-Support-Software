from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import time
from datetime import datetime
from overrides import overrides

from constants import Constants
from avionicsObject import AvionicsObject
from customLabel import CustomLabel


class Motor(AvionicsObject):
    """
    Class to handle all solenoid objects and their functionality
    """

    object_name = "Motor"

    def __init__(self, widget_parent: QWidget, position: QPointF, fluid: int, width: float = 70,
                 height: float = 78*1.5, name: str = "Motor",
                 scale: float = 1, serial_number: str = '',
                 long_name: str = 'Motor', is_vertical: bool = False,
                 locked: bool = False, position_locked: bool = False, _id: int = None,
                 serial_number_label_pos: str = "Right", serial_number_label_local_pos: QPointF = QPointF(0, 0),
                 serial_number_label_font_size: float = 10, long_name_label_pos: str = "Top",
                 long_name_label_local_pos: QPointF = QPointF(0, 0), long_name_label_font_size: float = 12,
                 long_name_label_rows: int = 1, channel: str = 'Undefined', board: str = 'Undefined',
                 long_name_visible:bool = True, serial_number_visible:bool = True):

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
        :param channel: the specific channel the device is plugged into
        :param board: the avionics board the device is plugged into
        """

        # TODO: Still bleah, should have a way to rotate or something

        super().__init__(parent=widget_parent, position=position, fluid=fluid, width=width, height=height,
                         name=name, is_vertical=is_vertical, scale=scale,
                         serial_number=serial_number, long_name=long_name, locked=locked,
                         position_locked=position_locked,
                         _id=_id, serial_number_label_pos=serial_number_label_pos,
                         serial_number_label_local_pos=serial_number_label_local_pos,
                         serial_number_label_font_size=serial_number_label_font_size,
                         long_name_label_pos=long_name_label_pos,
                         long_name_label_local_pos=long_name_label_local_pos,
                         long_name_label_font_size=long_name_label_font_size,
                         long_name_label_rows=long_name_label_rows,long_name_visible=long_name_visible,
                         serial_number_visible=serial_number_visible, board=board, channel=channel)


        self.window = self.widget_parent.window

        # The boxes the values go in
        self.boxWidth = 55 * self.gui.pixel_scale_ratio[0] * self.scale
        self.boxHeight = 20 * self.gui.pixel_scale_ratio[1] * self.scale

        # State tracks the motor values
        self.setPoint = 0
        self.currentPos = 0
        self.potPos = 0
        self.currenta = 0
        self.currentb = 0
        self.Pconstant = 0
        self.Iconstant = 0
        self.Dconstant = 0

        # Define the labels that keep track of position and set point
        self.set_pos_title_label = CustomLabel(self.widget_parent, self.gui, text="Set Pos")
        self.set_pos_title_label.setFixedWidth(self.width)
        self.set_pos_title_label.lower()

        self.set_pos_label = CustomLabel(self.widget_parent, self.gui, text=str(self.setPoint)+ "°")
        self.set_pos_label.setFixedSize(self.boxWidth, self.boxHeight)
        self.set_pos_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.set_pos_label.lower()

        self.current_pos_title_label = CustomLabel(self.widget_parent,self.gui, text="Curr Pos")
        self.current_pos_title_label.setFixedWidth(self.width)
        self.current_pos_title_label.lower()

        self.current_pos_label = CustomLabel(self.widget_parent, self.gui, text=str(self.currentPos)+ "°")
        self.current_pos_label.setFixedSize(self.boxWidth, self.boxHeight)
        self.current_pos_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.current_pos_label.lower()

        self.pot_pos_title_label = CustomLabel(self.widget_parent,self.gui, text="Pot Pos")
        self.pot_pos_title_label.setFixedWidth(self.width)
        self.pot_pos_title_label.lower()

        self.pot_pos_label = CustomLabel(self.widget_parent, self.gui, text=str(self.currentPos)+ "°")
        self.pot_pos_label.setFixedSize(self.boxWidth, self.boxHeight)
        self.pot_pos_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.pot_pos_label.lower()

        # Move labels to their positions
        self.moveLabelsToPosition()

        self.updateToolTip()

        self.gui.liveDataHandler.dataPacketSignal.connect(self.updateFromDataPacket)

    # TODO: Use this withe new configuration manager
    # @classmethod
    # def initFromObject(cls, object):

    def moveLabelsToPosition(self):
        """
        Move the motor labels to the correct position
        :return:
        """

        blankSpaceHeight = (self.height-self.boxHeight*3 - self.set_pos_title_label.height()*3)/4

        self.set_pos_title_label.setFixedWidth(self.width)
        self.set_pos_title_label.move(self.position.x(), self.position.y() + blankSpaceHeight * (1))

        self.set_pos_label.setFixedSize(self.boxWidth, self.boxHeight)
        self.set_pos_label.move(self.position.x() + (self.width - self.boxWidth)/2, self.set_pos_title_label.y() + self.set_pos_title_label.height())

        self.current_pos_title_label.setFixedWidth(self.width)
        self.current_pos_title_label.move(self.position.x(), self.position.y() + self.set_pos_title_label.height() + self.boxHeight + blankSpaceHeight * (2))

        self.current_pos_label.setFixedSize(self.boxWidth, self.boxHeight)
        self.current_pos_label.move(self.position.x() + (self.width - self.boxWidth)/2, self.current_pos_title_label.y() + self.current_pos_title_label.height())

        self.pot_pos_title_label.setFixedWidth(self.width)
        self.pot_pos_title_label.move(self.position.x(), self.position.y() + 2*self.current_pos_title_label.height() + 2*self.boxHeight + blankSpaceHeight * (3))

        self.pot_pos_label.setFixedSize(self.boxWidth, self.boxHeight)
        self.pot_pos_label.move(self.position.x() + (self.width - self.boxWidth)/2, self.pot_pos_title_label.y() + self.pot_pos_title_label.height())

    @overrides
    def draw(self):
        """
        Draws the solenoid icon on screen
        """

        # Holds the path of lines to draw
        path = QPainterPath()

        # Move path to starting position
        path.moveTo(0, 0)  # Top left corner

        path.addRect(0, 0, self.width, self.height)

        path.moveTo(self.width/2 - 1,self.height)

        path.lineTo(self.width/2 - 1,self.height+20*self.gui.pixel_scale_ratio[1])

        x1 = (self.width - self.boxWidth)/2
        x2 = x1 + self.boxWidth

        y1 = self.set_pos_title_label.y() - self.position.y() + self.set_pos_title_label.height()
        y2 = y1 + self.boxHeight

        y3 = self.current_pos_title_label.y()-self.position.y() + self.current_pos_title_label.height()
        y4 = y3 + self.boxHeight

        y5 = self.pot_pos_title_label.y()-self.position.y() + self.pot_pos_title_label.height()
        y6 = y5 + self.boxHeight

        path.moveTo(x1, y1)
        path.lineTo(x2, y1)
        path.lineTo(x2, y2)
        path.lineTo(x1, y2)
        path.lineTo(x1, y1)

        path.moveTo(x1, y3)
        path.lineTo(x2, y3)
        path.lineTo(x2, y4)
        path.lineTo(x1, y4)
        path.lineTo(x1, y3)

        path.moveTo(x1, y5)
        path.lineTo(x2, y5)
        path.lineTo(x2, y6)
        path.lineTo(x1, y6)
        path.lineTo(x1, y5)

        path.translate(self.position.x(), self.position.y())

        self.widget_parent.painter.drawPath(path)

        self.widget_parent.painter.setBrush(Qt.NoBrush)

        super().draw()

        # This is debug, draws a box around the origin of object
        # self.widget_parent.painter.fillRect(QRectF(self.position.x(), self.position.y(), 7, 7),Constants.fluidColor[self.fluid])

    @overrides
    def onClick(self):
        """
        When a solenoid is clicked this function is called
        """

        super().onClick()

        if not self.widget_parent.parent.is_editing:
            self.showMotorDialog()

        # Tells widget painter to update screen
        self.widget_parent.update()

    def showMotorDialog(self):
        """
        Shows a dialog when the motor is clicked. Allows the user to update the set point, zero and PID constants
        """
        # Create the dialog
        dialog = QDialog(self.window)
        dialog.setWindowTitle("Motor Set-points")
        dialog.setWindowModality(Qt.ApplicationModal)

        # Set dialog size and place in middle of window
        dialog.resize(450 * self.gui.pixel_scale_ratio[0], 240 * self.gui.pixel_scale_ratio[1])
        dialog.setMinimumWidth(450 * self.gui.pixel_scale_ratio[0])
        dialog.setMinimumWidth(240 * self.gui.pixel_scale_ratio[1])
        dialog.move((self.window.width() - dialog.width()) / 2,
                    (self.window.height() - dialog.height()) / 2)

        # Vertical layout to hold everything
        verticalLayout = QVBoxLayout(dialog)

        # Create the form layout that will hold the text box
        formLayout = QFormLayout()
        formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)  # This is properly resize textbox on OSX
        verticalLayout.addLayout(formLayout)

        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.default_font)
        font.setPointSize(14 * self.gui.font_scale_ratio)

        # Create spin boxes
        setPointBox = QDoubleSpinBox()
        setPointBox.setDecimals(1)
        setPointBox.setMinimum(-2999.9)
        setPointBox.setMaximum(2999.9)
        setPointBox.setValue(self.setPoint)
        setPointBox.setFont(font)

        PPointBox = QDoubleSpinBox()
        PPointBox.setMaximum(599.99)
        PPointBox.setValue(self.Pconstant)
        PPointBox.setDecimals(2)
        PPointBox.setFont(font)

        IPointBox = QDoubleSpinBox()
        IPointBox.setMaximum(599.99)
        IPointBox.setValue(self.Iconstant)
        IPointBox.setDecimals(2)
        IPointBox.setFont(font)

        DPointBox = QDoubleSpinBox()
        DPointBox.setMaximum(599.99)
        DPointBox.setValue(self.Dconstant)
        DPointBox.setDecimals(2)
        DPointBox.setFont(font)


        # Create zero button
        zeroBtn = QPushButton("Zero Motor")
        zeroBtn.setDefault(False)
        zeroBtn.setAutoDefault(False)
        zeroBtn.clicked.connect(lambda: self.motorDialogZeroButtonClicked(spinBoxes, dialog))

        # Create zero pot button
        zeroPotBtn = QPushButton("Zero Pot")
        zeroPotBtn.setDefault(False)
        zeroPotBtn.setAutoDefault(False)
        zeroPotBtn.clicked.connect(self.motorDialogZeroPotButtonClicked)

        spinBoxes = [setPointBox, PPointBox, IPointBox, DPointBox]

        label1 = QLabel("Set Point:")
        label1.setFont(font)
        label2 = QLabel("P Constant:")
        label2.setFont(font)
        label3 = QLabel("I Constant:")
        label3.setFont(font)
        label4 = QLabel("D Constant:")
        label4.setFont(font)
        label5 = QLabel("Zero Motor:")
        label5.setFont(font)
        label6 = QLabel("Zero Pot:")
        label6.setFont(font)
        # Add to the layout
        formLayout.addRow(label1, setPointBox)
        formLayout.addRow(label2, PPointBox)
        formLayout.addRow(label3, IPointBox)
        formLayout.addRow(label4, DPointBox)
        formLayout.addRow(label5, zeroBtn)
        formLayout.addRow(label6, zeroPotBtn)

        # Horizontal button layout
        buttonLayout = QHBoxLayout()
        # Create the buttons, make sure there is no default option, and connect to functions
        cancel_button = QPushButton("Cancel")
        cancel_button.setFont(font)
        cancel_button.setDefault(False)
        cancel_button.setAutoDefault(False)
        cancel_button.clicked.connect(lambda: dialog.done(1))
        cancel_button.setFixedWidth(125 * self.gui.pixel_scale_ratio[0])  # Lazy way to make buttons not full width

        save_button = QPushButton("Save")
        save_button.setFont(font)
        save_button.setDefault(False)
        save_button.setAutoDefault(False)
        save_button.clicked.connect(lambda: self.motorDialogSave(spinBoxes, dialog))
        save_button.setFixedWidth(125 * self.gui.pixel_scale_ratio[0])

        buttonLayout.addWidget(cancel_button)
        buttonLayout.addWidget(save_button)

        verticalLayout.addLayout(buttonLayout)

        dialog.show()

    def motorDialogZeroButtonClicked(self, spinBoxes, dialog): #TODO: update
        """
        Function called when the zero button is clicked in motor dialog
        """
        if self.gui.debug_mode:
            self.updateValues(self.currenta,self.currentb, 0,self.potPos,self.setPoint,self.Pconstant,self.Iconstant,self.Dconstant)
        else:
            if self.isAvionicsFullyDefined():
                cmd_dict = {
                    "function_name": "set_stepper_zero",
                    "target_board_addr": self.widget_parent.window.interface.getBoardAddr(self.avionics_board),
                    "timestamp": int(datetime.now().timestamp()),
                    "args": [int(self.channel)]
                }
                #print(cmd_dict)
                self.gui.liveDataHandler.sendCommand(3, cmd_dict)
                spinBoxes[0].setValue(0)
    
    def motorDialogZeroPotButtonClicked(self): #TODO: update
        """
        Function called when the zero pot button is clicked in motor dialog
        """
        if self.gui.debug_mode:
            self.updateValues(self.currenta,self.currentb, self.currentPos,0,self.setPoint,self.Pconstant,self.Iconstant,self.Dconstant)
        else:
            if self.isAvionicsFullyDefined():
                cmd_dict = {
                    "function_name": "ambientize_pot",
                    "target_board_addr": self.widget_parent.window.interface.getBoardAddr(self.avionics_board),
                    "timestamp": int(datetime.now().timestamp()),
                    "args": [int(self.channel)]
                }
                #print(cmd_dict)
                self.gui.liveDataHandler.sendCommand(3, cmd_dict)

    def motorDialogSave(self, spinBoxes, dialog):
        """
        Saves the new motor values and sends the commands to the board
        :param spinBoxes: spin boxes with the values
        :param dialog: dialog with motor settings
        """
        setpoint = spinBoxes[0].value()
        p = spinBoxes[1].value()
        i = spinBoxes[2].value()
        d = spinBoxes[3].value()

        if self.gui.debug_mode:
            self.updateValues(self.currenta,self.currentb,self.currentPos,self.potPos,setpoint,p,i,d)
        else:
            if self.isAvionicsFullyDefined():
                cmd_dict = {
                    "function_name": "set_stepper_pos",
                    "target_board_addr": self.widget_parent.window.interface.getBoardAddr(self.avionics_board),
                    "timestamp": int(datetime.now().timestamp()),
                    "args": [int(self.channel), float(setpoint)]
                }
                self.gui.liveDataHandler.sendCommand(3, cmd_dict)
                time.sleep(0.1)
                cmd_dict = {
                    "function_name": "set_kp",
                    "target_board_addr": self.widget_parent.window.interface.getBoardAddr(self.avionics_board),
                    "timestamp": int(datetime.now().timestamp()),
                    "args": [int(self.channel), float(p)]
                }
                self.gui.liveDataHandler.sendCommand(3, cmd_dict)
                time.sleep(0.1)
                cmd_dict = {
                    "function_name": "set_ki",
                    "target_board_addr": self.widget_parent.window.interface.getBoardAddr(self.avionics_board),
                    "timestamp": int(datetime.now().timestamp()),
                    "args": [int(self.channel), float(i)]
                }
                self.gui.liveDataHandler.sendCommand(3, cmd_dict)
                time.sleep(0.1)
                cmd_dict = {
                    "function_name": "set_kd",
                    "target_board_addr": self.widget_parent.window.interface.getBoardAddr(self.avionics_board),
                    "timestamp": int(datetime.now().timestamp()),
                    "args": [int(self.channel), float(d)]
                }
                self.gui.liveDataHandler.sendCommand(3, cmd_dict)
        dialog.done(2)

    def updateValues(self, currenta, currentb, currPos, potPos, setPoint, Pconstant, Iconstant, Dconstant):
        """
        Updates the current motor values from passed data packet values
        """
        self.currenta = currenta
        self.currentb = currentb
        self.currentPos = currPos
        self.potPos = potPos
        self.setPoint = setPoint
        self.Pconstant = Pconstant
        self.Iconstant = Iconstant
        self.Dconstant = Dconstant

        # Update labels
        self.set_pos_label.setText(str(self.setPoint)+ "°", False)
        self.current_pos_label.setText(str(self.currentPos) + "°", False)
        self.pot_pos_label.setText(str(self.potPos) + "°", False)

        self.updateToolTip()

    @overrides
    def setScale(self, scale):
        """
        Calls super set scale, need this here to update the box width and height
        :param scale: new scale
        """
        super().setScale(scale)

        self.boxWidth = 55 * self.gui.pixel_scale_ratio[0] * self.scale
        self.boxHeight = 20 * self.gui.pixel_scale_ratio[1] * self.scale

        # Make the font bigger when scaled upwards
        font = self.set_pos_title_label.font()
        font.setPointSizeF(14 * scale * self.gui.font_scale_ratio)

        self.set_pos_label.setFont(font)
        self.set_pos_title_label.setFont(font)
        self.set_pos_title_label.setFixedSize_()

        self.current_pos_label.setFont(font)
        self.current_pos_title_label.setFont(font)
        self.current_pos_title_label.setFixedSize_()

        self.pot_pos_label.setFont(font)
        self.pot_pos_title_label.setFont(font)
        self.pot_pos_title_label.setFixedSize_()

        # Update Labels
        self.moveLabelsToPosition()

    @overrides
    def move(self, point: QPoint):
        """
        Calls super, moves the labels
        :param point: new point to move to
        """
        super().move(point)

        self.moveLabelsToPosition()

    def updateToolTip(self):
        """
        Called to update the tooltip of the solenoid
        """

        text = ""

        if self.isAvionicsFullyDefined():
            text += "Channel: %s\n" % (self.getBoardChannelString())
        else:
            text += "Channel:\n"

        # text += "Currenta: " + str(self.currenta) + "A\n"
        # text += "Currentb: " + str(self.currentb) + "A\n"
        text += "P constant: " + str(self.Pconstant) +"\n"
        text += "I constant: " + str(self.Iconstant) +"\n"
        text += "D constant: " + str(self.Dconstant)

        self.setToolTip_(text)

    @overrides
    def lowerObject(self):
        """
        Lowers the object, overridden to make sure the callout labels does not get in the way
        """
        super().lowerObject()

        # Lower the labels
        self.set_pos_title_label.lower()
        self.set_pos_label.lower()
        self.current_pos_title_label.lower()
        self.current_pos_label.lower()
        self.pot_pos_title_label.lower()
        self.pot_pos_label.lower()

    @overrides
    def setMouseEventTransparency(self, should_be_transparent):
        """
        Sets the object to be transparent to mouse or not, overridden for motor pos/ pot labels
        :param should_be_transparent:
        """
        super().setMouseEventTransparency(should_be_transparent)
        self.set_pos_label.setAttribute(Qt.WA_TransparentForMouseEvents, should_be_transparent)
        self.set_pos_title_label.setAttribute(Qt.WA_TransparentForMouseEvents, should_be_transparent)

        self.current_pos_label.setAttribute(Qt.WA_TransparentForMouseEvents, should_be_transparent)
        self.current_pos_title_label.setAttribute(Qt.WA_TransparentForMouseEvents, should_be_transparent)

        self.pot_pos_label.setAttribute(Qt.WA_TransparentForMouseEvents, should_be_transparent)
        self.pot_pos_title_label.setAttribute(Qt.WA_TransparentForMouseEvents, should_be_transparent)

    @overrides
    def deleteSelf(self):
        """
        Delete itself
        """
        self.set_pos_label.deleteLater()
        self.set_pos_title_label.deleteLater()
        self.current_pos_label.deleteLater()
        self.current_pos_title_label.deleteLater()
        self.pot_pos_label.deleteLater()
        self.pot_pos_title_label.deleteLater()
        del self.set_pos_label
        del self.set_pos_title_label
        del self.current_pos_label
        del self.current_pos_title_label
        del self.pot_pos_label
        del self.pot_pos_title_label

        super().deleteSelf()

    @pyqtSlot(object)
    def updateFromDataPacket(self, data_packet: dict):

        if self.isAvionicsFullyDefined():
            board_prefix = self.gui.controlsWindow.interface.getPrefix(self.avionics_board)
            channel_name = board_prefix + "mtr" + str(self.channel)

            # curra = data_packet[channel_name + ".ia"]
            # currb = data_packet[channel_name + ".ib"]
            curra = 0
            currb = 0
            pos = data_packet[channel_name + ".pos"]
            pot_pos = data_packet[board_prefix+"pot" + str(self.channel)+".e"]  # i hate u avionics
            setp = data_packet[channel_name + ".set"]
            p = data_packet[channel_name + ".kp"]
            i = data_packet[channel_name + ".ki"]
            d = data_packet[channel_name + ".kd"]
            self.updateValues(curra, currb, pos, pot_pos, setp, p, i, d)