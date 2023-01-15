from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt

from s2Interface import S2_Interface

INTERFACE = S2_Interface()
CHANNELS = INTERFACE.channels

class QHLine(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class QVLine(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.VLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class TankWidget(QtWidgets.QWidget):
    progressChanged = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0.10

    @QtCore.pyqtProperty(float, notify=progressChanged)
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, p):
        if 0 <= p <= 1.0:
            self._progress = p
            self.progressChanged.emit(p)
            self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        height = self.progress * self.height()

        r = QtCore.QRect(0, self.height() - height, self.width(), height)
        painter.fillRect(r, QtGui.QBrush(Qt.blue))
        pen = QtGui.QPen(QtGui.QColor("black"), 4)
        painter.setPen(pen)
        painter.drawRect(self.rect())

    def sizeHint(self):
        return QtCore.QSize(100, 100)


class LevelWidget(QtWidgets.QGroupBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        left_layout = QtWidgets.QGridLayout()
        layout.addLayout(left_layout)
        layout.addWidget(QVLine())
        right_layout = QtWidgets.QVBoxLayout()
        layout.addLayout(right_layout)
        
        self.tank = TankWidget()
        right_layout.addWidget(self.tank)

        completer = QtWidgets.QCompleter(CHANNELS)
        completer.setCaseSensitivity(False)
        completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        
        plabel = QtWidgets.QLabel("Pressure:")
        self.pvalue = QtWidgets.QLabel("XXX.X")
        punit = QtWidgets.QLabel("PSIG")
        self.pchannel = QtWidgets.QComboBox()
        self.pchannel.setEditable(True)
        self.pchannel.addItems([""]+CHANNELS)
        self.pchannel.setCompleter(completer)
        self.pchannel.lineEdit().setAlignment(Qt.AlignBottom)
        left_layout.addWidget(plabel, 0, 0)
        left_layout.addWidget(self.pvalue, 0, 1)
        left_layout.addWidget(punit, 0, 2)
        left_layout.addWidget(self.pchannel, 0, 3)

        tlabel = QtWidgets.QLabel("Temperature:")
        self.tvalue = QtWidgets.QLabel("XXX.X")
        tunit = QtWidgets.QLabel("PSIG")
        self.tchannel = QtWidgets.QComboBox()
        self.tchannel.setEditable(True)
        self.tchannel.addItems([""]+CHANNELS)
        self.tchannel.setCompleter(completer)
        self.tchannel.lineEdit().setAlignment(Qt.AlignBottom)
        left_layout.addWidget(tlabel, 1, 0)
        left_layout.addWidget(self.tvalue, 1, 1)
        left_layout.addWidget(tunit, 1, 2)
        left_layout.addWidget(self.tchannel, 1, 3)

        dplabel = QtWidgets.QLabel("DP:")
        self.dpvalue = QtWidgets.QLabel("XXX.X")
        dpunit = QtWidgets.QLabel("PSIG")
        self.dpchannel = QtWidgets.QComboBox()
        self.dpchannel.setEditable(True)
        self.dpchannel.addItems([""]+CHANNELS)
        self.dpchannel.setCompleter(completer)
        self.dpchannel.lineEdit().setAlignment(Qt.AlignBottom)
        left_layout.addWidget(dplabel, 2, 0)
        left_layout.addWidget(self.dpvalue, 2, 1)
        left_layout.addWidget(dpunit, 2, 2)
        left_layout.addWidget(self.dpchannel, 2, 3)

        htlabel = QtWidgets.QLabel("Target Height:")
        self.htvalue = QtWidgets.QLineEdit()
        htunit = QtWidgets.QLabel("in")
        left_layout.addWidget(htlabel, 3, 0)
        left_layout.addWidget(self.htvalue, 3, 1)
        left_layout.addWidget(htunit, 3, 2)

        self.isobar_check = QtWidgets.QCheckBox("Isobaric Density",)
        self.isobar_check.setChecked(True)
        self.isobar_check.setEnabled(False)
        left_layout.addWidget(self.isobar_check, 4, 0, 1, 4)

        left_layout.addWidget(QHLine(), 5, 0, 1, 4)

        dlabel = QtWidgets.QLabel("Density:")
        self.dvalue = QtWidgets.QLabel("XXX.X")
        dunit = QtWidgets.QLabel("kg/m^3")
        left_layout.addWidget(dlabel, 6, 0)
        left_layout.addWidget(self.dvalue, 6, 1)
        left_layout.addWidget(dunit, 6, 2)

        hlabel = QtWidgets.QLabel("Height:")
        self.hvalue = QtWidgets.QLabel("XXX.X")
        hunit = QtWidgets.QLabel("in")
        left_layout.addWidget(hlabel, 7, 0)
        left_layout.addWidget(self.hvalue, 7, 1)
        left_layout.addWidget(hunit, 7, 2)

        left_layout.setColumnStretch(0, 1)
        left_layout.setColumnStretch(1, 1)
        left_layout.setColumnStretch(2, 1)
        left_layout.setColumnStretch(3, 2)

    def update_values(self, last_packet):
        pc = self.pchannel.currentText()
        if pc in CHANNELS:
            p = last_packet[pc]
            self.pvalue.setText(str(p))
        else:
            p = None
        
        tc = self.tchannel.currentText()
        if tc in CHANNELS:
            t = last_packet[tc]
            self.tvalue.setText(str(t))
        else:
            t = None

        dpc = self.dpchannel.currentText()
        if dpc in CHANNELS:
            dp = last_packet[dpc]
            self.dpvalue.setText(str(dp))
        else:
            dp = None
        
        #if p and t and dpc:
        if t != None and dp != None:
            # calculate level
            d = -0.0169*t**2 - 1.9296*t + 1056.7 # density in kg/m^3 from refprop
            h = (dp*6894.757/(d*9.81))*39.37 # height in inches
            self.dvalue.setText(str(d))
            self.hvalue.setText(str(h))

            try: # try and update tank level indicator
                ht = float(self.htvalue.text())
                ff = h/ht
                self.tank.progress = ff
            except:
                #traceback.print_exc()
                pass

            
class TankLevelDialog(QtWidgets.QDialog):
    def __init__(self, dual=False, gui=None):
        super().__init__()
        self._dual = dual
        self.gui = gui

        if self.gui is not None:
            self.gui.liveDataHandler.dataPacketSignal.connect(self.updateFromDataPacket)

        self.setWindowTitle("Tank Level Calculator")
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)   
        
        self.level0 = LevelWidget()
        self.level0.setTitle("Tank 0")
        layout.addWidget(self.level0)

        if self._dual:
            layout.addWidget(QHLine())
            self.level1 = LevelWidget()
            self.level1.setTitle("Tank 1")
            layout.addWidget(self.level1)
            #self.setStyleSheet("QGroupBox {  border: 0.5px solid black;}")
    
    def update_values(self, last_packet):
        self.level0.update_values(last_packet)
        
        if self._dual:
            self.level1.update_values(last_packet)

    @QtCore.pyqtSlot(object)
    def updateFromDataPacket(self, data_packet: dict):
        self.update_values(data_packet)
  

# if __name__ == "__main__":
#     QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
#     QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
#     if not QtWidgets.QApplication.instance():
#         app = QtWidgets.QApplication(sys.argv)
#     else:
#         app = QtWidgets.QApplication.instance()
#
#     # initialize application
#     APPID = 'MASA.AutoManager'  # arbitrary string
#     if os.name == 'nt':  # Bypass command because it is not supported on Linux
#         ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
#     else:
#         pass
#         # NOTE: On Ubuntu 18.04 this does not need to done to display logo in task bar
#     app.setWindowIcon(QtGui.QIcon('Images/logo_server.png'))
#
#     window = TankLevelDialog(dual = False)
#     window.show()
#     sys.exit(app.exec())
