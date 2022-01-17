from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from ClientWidget import ClientWidget
import time


class LiveDataHandler:

    def __init__(self, gui: None):

        self._gui = gui
        self._client = None
        self.thread = LiveDataHandlerBackgroundThread(self)
        self.campaign = self._gui.campaign

        self.dataPacketSignal = self.thread.lastPacketDataSignal
        self.updateScreenSignal = self.thread.updateScreenSignal
        self.connectionStatusSignal = self.thread.connectionStatusSignal

        self.is_active = False  # Use this to check if the run is running

    def postInit(self):
        self._initClient()

    def _initClient(self):
        self._client = ClientWidget(True, self._gui)
        self.startThread()

    def sendCommand(self, cmd_id: int, args: dict):
        self._client.command(cmd_id, args)

    def getClient(self):
        return self._client

    def getGui(self):
        return self._gui

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
            time.sleep(0.2)
            packet = self.dataHandler.getClient().cycle()

            # Not really data updating but oh well
            self.dataHandler.getGui().controlsWindow.button_box.cycle()

            if packet is not None:
                # All is well
                if self.dataHandler.getClient().is_connected and packet["actively_rx"]:
                    self.connectionStatusSignal.emit(0, packet["error_msg"], self.dataHandler.getClient().is_commander)
                # Server to GUI connection is good, but data should be coming from board, but it is bad or is delayed
                elif self.dataHandler.getClient().is_connected and packet["ser_open"]:
                    self.connectionStatusSignal.emit(1, packet["error_msg"], self.dataHandler.getClient().is_commander)
                # Server to GUI connection is good, but there is no open serial (no way for pacets to be recieved)
                elif self.dataHandler.getClient().is_connected and not packet["ser_open"]:
                    self.connectionStatusSignal.emit(2, packet["error_msg"], self.dataHandler.getClient().is_commander)

                if self.dataHandler.campaign.is_active:
                    # TODO: Not sure if this goes here, or under actively_rx, seem weird to try to push bad data
                    # {"gse.vlv0.en": 1, "gse.vlv0.e": 12, "gse.vlv0.i": 2, "gse.e_batt": 11.1, "gse.ibus": .12,
                    #                          "gse.STATE": 0, "gse.LOGGING_ACTIVE": 1, "gse.timestamp": 102242, "gse.adc_rate": 200,
                    #                          "gse.telem_rate": 10, "gse.flash_mem": 1053, "time": 353}
                    self.lastPacketDataSignal.emit(packet)  # change to packet when ready

            else:
                # Server to GUI connection bad, no info to display at the time
                self.connectionStatusSignal.emit(3, "", self.dataHandler.getClient().is_commander)

            self.updateScreenSignal.emit()

            if not self.dataHandler.is_active:
                break


