from PyQt5.QtCore import *

import time

"""
This file contains the class and functions to handle the 'run' or test being conducted
"""


# class Campaign:
#
#     def __init__(self):
#         """
#         Initializes the run, this is called at program start so it holds no data until the run is actually started. It
#         has to be done at the GUI launch instead of when the user starts to run to ensure that slots signals and events
#         can be properly connected
#         """
#
#         """
#         :var is_active: Holds if the run is currently active or not
#         :var startDate: The start date of the run, given in the timezone of the computer
#         :var startTime: The start time of the run, given in the timezone of the computer
#         :var CET: The mission elapsed time for this run/ test in milliseconds
#         :var saveName: The name that will be used to title files
#         """
#         super().__init__()
#
#         # All of these are set to none to make sure if someone access before it is created it fails
#         self.title = None
#         self.is_active = False  # Use this to check if the run is running
#         self.startDateTime = None
#         self.CET = None
#         self.saveName = None
#         self.thread = None
#         self.client = None

from liveDataHandler import LiveDataHandler

class Campaign(QObject):  #
    """
    Class that holds all the functions for a new campaign
    """

    # HMM: We only want one instance of this class ever so do we make it a Singleton?!
    # TODO: Currently the Gui will have to be closed and reopened to allow for a new run

    # Signals for this class
    campaignStartSignal = pyqtSignal()
    campaignEndSignal = pyqtSignal()
    updateCETSignal = pyqtSignal(int)

    def __init__(self):
        """
        Initializes the run, this is called at program start so it holds no data until the run is actually started. It
        has to be done at the GUI launch instead of when the user starts to run to ensure that slots signals and events
        can be properly connected
        """

        """
        :var is_active: Holds if the run is currently active or not
        :var startDate: The start date of the run, given in the timezone of the computer
        :var startTime: The start time of the run, given in the timezone of the computer
        :var CET: The mission elapsed time for this run/ test in milliseconds
        :var saveName: The name that will be used to title files
        """
        super().__init__()

        # All of these are set to none to make sure if someone access before it is created it fails
        self.title = None
        self.is_active = False  # Use this to check if the run is running
        self.startDateTime = None
        self.CET = None
        self.saveName = None
        self.thread = CampaignBackgroundThread(self)
        self.dataPacketSignal = self.thread.lastPacketDataSignal
        self.updateScreenSignal = self.thread.updateScreenSignal
        self.connectionStatusSignal = self.thread.connectionStatusSignal

        self.client = None

    def startRun(self, title: str):
        """
        Start the run, this just populates the pre-initialized variables
        :param title: the title for this test
        :return:
        """
        self.title = title

        if self.client:
            self.client.command(6, str(title))  # TODO: input validation

        self.is_active = True
        self.startDateTime = QDateTime.currentDateTime()
        self.CET = 0
        self.saveName = self.startDateTime.date().toString("yyyy-MM-dd") + "-T" + \
                                self.startDateTime.time().toString("hhmm") + "__" + self.title.replace(" ", "_")

        self.campaignStartSignal.emit()

    def endRun(self):
        """
        End the current run
        """
        # Want to update CET one last time to get final CET before run ends
        self.updateCET()
        self.is_active = False
        self.campaignEndSignal.emit()
        if self.client:
            self.client.command(6, None)

        # Reset, and then restart thread
        self.CET = None
        self.startThread()

    def updateCET(self):
        """
        This function updates the CET time for the run. Should be called whenever the CET being accurate is critical
        """
        # Have to double check this here because thread is still in loop when run ends and one last CET update occurs
        if self.is_active:
            # Set the CET, note the msecTo function returns negative for times in the past
            self.CET = -1 * QDateTime.currentDateTime().msecsTo(self.startDateTime)
            # Emit the signal that will allow other parts of the GUI to update with this data
            self.updateCETSignal.emit(self.CET)
    
    def setClient(self, client):
        self.client = client

    def startThread(self):
        self.thread.start()


# TODO: Still don't like orginization of this ahhh, feels like this is just a background server handler basically
class CampaignBackgroundThread(QThread):
    """
    Class that handles background threading for the run class, this is to prevent the GUI from hanging
    """

    lastPacketDataSignal = pyqtSignal(object)
    updateScreenSignal = pyqtSignal()
    connectionStatusSignal = pyqtSignal(int, str, bool)

    def __init__(self, campaign):
        """
        Initializer
        :param run: The run instance that is currently active
        """
        super().__init__()
        self.campaign = campaign

    def run(self):
        """
        This is the function that is constantly running in the background
        """

        # While the run is active keep the thread alive, will cleanly exit when run stops
        while True:
            # Update the CET every second, this can be increased but seems unnecessary
            time.sleep(0.2)
            packet = self.campaign.client.cycle()

            # TODO: This is only active if someone starts the run, server feedback should not depend on that
            if packet is not None:
                # All is well
                if self.campaign.client.is_connected and packet["actively_rx"]:
                    self.connectionStatusSignal.emit(0,packet["error_msg"], self.campaign.client.is_commander)
                # Server to GUI connection is good, but data should be coming from board, but it is bad or is delayed
                elif self.campaign.client.is_connected and packet["ser_open"]:
                    self.connectionStatusSignal.emit(1, packet["error_msg"], self.campaign.client.is_commander)
                # Server to GUI connection is good, but there is no open serial (no way for pacets to be recieved)
                elif self.campaign.client.is_connected and not packet["ser_open"]:
                    self.connectionStatusSignal.emit(2, packet["error_msg"], self.campaign.client.is_commander)

                if self.campaign.is_active:
                    # TODO: Not sure if this goes here, or under actively_rx, seem weird to try to push bad data
                    # {"gse.vlv0.en": 1, "gse.vlv0.e": 12, "gse.vlv0.i": 2, "gse.e_batt": 11.1, "gse.ibus": .12,
                    #                          "gse.STATE": 0, "gse.LOGGING_ACTIVE": 1, "gse.timestamp": 102242, "gse.adc_rate": 200,
                    #                          "gse.telem_rate": 10, "gse.flash_mem": 1053, "time": 353}
                    self.lastPacketDataSignal.emit(packet)  # change to packet when ready

            else:
                # Server to GUI connection bad, no info to display at the time
                self.connectionStatusSignal.emit(3, "", self.campaign.client.is_commander)

            if self.campaign.is_active:
                self.campaign.updateCET()
            elif not self.campaign.is_active and self.campaign.CET is not None:
                self.updateScreenSignal.emit()
                break

            self.updateScreenSignal.emit()

