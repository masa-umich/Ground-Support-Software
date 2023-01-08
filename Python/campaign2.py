import time

from PyQt5.QtCore import *
from constants import Constants
import math
import os
import json
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR
from typing import TextIO


class Campaign2(QObject):

    def __init__(self):
        super().__init__()

        self.isActive = False
        self.isTestActive = None
        self.title = None
        self.configurationData: dict = None
        self.avionicsMappings: dict = None

        self.test_history = []

        self.startDateTime = None
        self.CET = None
        self.TET = None

        self.campaignLocation = None

        self.saveName = None
        self.test_dict = {}

        self.campaignLog: TextIO = None
        self.testLog: TextIO = None

        # Save name
        self.lastRecoveredCampaign: str = None

        self.backgroundThread = CampaignBackgroundThread(self)

    def openCampaignLog(self, isRecovered: bool = False):

        self.campaignLocation = Constants.campaign_data_dir + self.saveName + "_2/"
        print(self.saveName)
        print(self.campaignLocation)

        if isRecovered:
            self.campaignLog = open(self.campaignLocation + "campaign_log.txt", "a+")

        else:
            # Create test folder
            if not os.path.isdir(self.campaignLocation + "tests/"):
                os.makedirs(self.campaignLocation + "tests/")

            self.campaignLog = open(self.campaignLocation + "campaign_log.txt", "w")
            self.campaignLog.write("Campaign started with save name: " + self.saveName + "\n")

            # Write configuration to file
            with open(self.campaignLocation + "configuration.json", "w") as write_file:
                json.dump(self.configurationData, write_file, indent="\t")
                os.chmod(write_file.name, S_IREAD | S_IRGRP | S_IROTH)

            # Write avionics mappings to file
            with open(self.campaignLocation + "avionicsMappings.csv", "w") as write_file:
                write_file.write("Channel,Name\n")
                for key in self.avionicsMappings:
                    if key != "Boards":  # currently don't list the boards the user has added
                        write_file.write(self.avionicsMappings[key][1] + "," + self.avionicsMappings[key][
                            0] + "\n")  # key is not useful, first index is name, second is channel
                os.chmod(write_file.name, S_IREAD | S_IRGRP | S_IROTH)

    def startCampaign(self, saveName: str, configurationData: dict, avionicsMappings: dict):
        if self.isActive:
            print("Campaign already active")
            return
        self.configurationData = configurationData
        self.avionicsMappings = avionicsMappings
        self.isActive = True
        # Lame and fix
        self.title = saveName.split("__")[1]
        self.startDateTime = QDateTime.currentDateTime()
        self.CET = 0
        self.saveName = saveName
        self.openCampaignLog()
        self.backgroundThread.start()

    def endCampaign(self):
        self.isActive = False
        self.CET = None
        self.title = None
        self.startDateTime = None
        self.saveName = None

    def CETasString(self):
        """
        Takes the CET and returns as a string
        :return: CET string
        """

        qTime = QTime(0, 0, 0)
        qtime = qTime.addSecs(math.floor(self.CET / 1000.0))
        return qtime.toString("hh:mm:ss")


class CampaignBackgroundThread(QThread):

    def __init__(self, campaign: Campaign2):
        super().__init__()

        self.campaign = campaign

    def run(self):

        while self.campaign.isActive:
            self.campaign.CET = -1 * QDateTime.currentDateTime().msecsTo(self.campaign.startDateTime)

            time.sleep(0.2)




