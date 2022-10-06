from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from ClientWidget import ClientWidget
from constants import Constants
import time


class LiveDataHandler:

    def __init__(self, gui: None):

        self._gui = gui
        self._client = ClientWidget(True, self._gui)
        self.is_active = False  # Use this to check if the thread is running

        self.thread = LiveDataHandlerBackgroundThread(self)
        self.startThread()
        self.sendAndPopulateData = False

        self.dataPacketSignal = self.thread.lastPacketDataSignal
        self.updateScreenSignal = self.thread.updateScreenSignal
        self.connectionStatusSignal = self.thread.connectionStatusSignal

    def sendCommand(self, cmd_id: int, args: dict):
        # TODO: Option to force commands through
        if self.sendAndPopulateData:
            self._client.command(cmd_id, args)

    def getClient(self):
        return self._client  # type: ClientWidget

    def getGui(self):
        return self._gui

    def setSendAndPopulateData(self, value: bool):
        self.sendAndPopulateData = value

    def shouldSendAndPopulateData(self):
        return self.sendAndPopulateData

    def startThread(self):
        self.is_active = True
        self.thread.start()


# TODO: Still don't like orginization of this ahhh, feels like this is just a background server handler basically
class LiveDataHandlerBackgroundThread(QThread):
    """
    Class that handles background threading for the run class, this is to prevent the GUI from hanging
    """

    lastPacketDataSignal = pyqtSignal(object)
    updateScreenSignal = pyqtSignal()
    connectionStatusSignal = pyqtSignal(int, str, bool)

    def __init__(self, dataHandler):
        """
        Initializer
        :param run: The run instance that is currently active
        """
        super().__init__()
        self.dataHandler = dataHandler

    def run(self):
        """
        This is the function that is constantly running in the background
        """

        # While the run is active keep the thread alive, will cleanly exit when run stops
        while True:
            # Check for data ever 200ms
            time.sleep(Constants.dataHandlerUpdateRate/1000)  # convert to seconds
            packet = self.dataHandler.getClient().cycle()

            if packet is not None:
                # All is well
                self.dataHandler.setSendAndPopulateData(True)

                if self.dataHandler.getClient().is_connected and packet["actively_rx"]:
                    self.connectionStatusSignal.emit(0, packet["error_msg"], self.dataHandler.getClient().is_commander)
                # Server to GUI connection is good, but data should be coming from board, but it is bad or is delayed
                elif self.dataHandler.getClient().is_connected and packet["ser_open"]:
                    self.connectionStatusSignal.emit(1, packet["error_msg"], self.dataHandler.getClient().is_commander)
                # Server to GUI connection is good, but there is no open serial (no way for pacets to be recieved)
                elif self.dataHandler.getClient().is_connected and not packet["ser_open"]:
                    self.connectionStatusSignal.emit(2, packet["error_msg"], self.dataHandler.getClient().is_commander)

                if self.dataHandler.shouldSendAndPopulateData() or self.dataHandler.getGui().debug_mode:
                    self.lastPacketDataSignal.emit(packet)

            else:

                if self.dataHandler.getClient().is_connected:
                    # For reasons unknown, it thinks it connected, but getting no packets. Display this
                    self.connectionStatusSignal.emit(4, "", self.dataHandler.getClient().is_commander)
                else:
                    # Server to GUI connection bad, no info to display at the time
                    self.connectionStatusSignal.emit(3, "", self.dataHandler.getClient().is_commander)

            self.updateScreenSignal.emit()

            if not self.dataHandler.is_active:
                break


