import time

from PyQt5.QtCore import *
from constants import Constants
import math
import os
import json
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR
from typing import TextIO
from termcolor import colored


class Campaign2(QObject):

    def __init__(self, server):
        super().__init__()

        self.server = server
        self.isActive = False
        self.isTestActive = None
        self.title = None
        self.configurationData: dict = None
        self.avionicsMappings: dict = None

        self.test_history = []

        self.startDateTime = None
        self.CET = None
        self.TET = None

        self.campaign_location = None

        self.saveName = None
        self.test_dict = {}

        self.campaign_log: TextIO = None
        self.testLog: TextIO = None

        # Save name
        self.lastRecoveredCampaign: str = None

        self.backgroundThread = CampaignBackgroundThread(self)

    # def update_campaign_logging(self, campaign_save_name: str, configuration_data: dict = None, avionics_mappings: dict = None):
    #     """
    #     Functions updates (starts/ stops) campaign logging. On start config data and avionics mappings are also sent. If
    #     filename is passed as None then it stops the campaign and starts general logging. If the filename is not none,
    #     but the configuration data and avionics mappings are, that means the server should recover the campaign
    #     :param campaign_save_name: save name of campaign
    #     :param configuration_data: dict of configuration data
    #     :param avionics_mappings: dict of avionics mappings
    #     :return: None
    #     """
    #
    #     self.closeLogs()
    #
    #     # No campaign, revert to general logging
    #     if campaign_save_name is None:
    #         file_timestamp = self.get_file_timestamp_string()
    #         self.server.open_base_logs(file_timestamp, self.server.working_directory + file_timestamp + "/", False)
    #         self.server.logSignal.emit("Server", "Raw server logging started under '%s'" % file_timestamp)
    #
    #     elif configuration_data is None and avionics_mappings is None:  # Check if function call matches recovered state
    #
    #         self.campaign_location = Constants.campaign_data_dir + campaign_save_name + "/"
    #
    #         # If this exists then we know we are properly recoverable, otherwise something bad happened
    #         campaign_dir_exists = os.path.isdir(self.campaign_location)
    #
    #         if not campaign_dir_exists:
    #             print(colored("WARNING: Recovered state requested, directory not found"), 'red')
    #             self.statusBarMessageSignal.emit("Campaign recovery failed. See terminal", True)
    #             # Restart logging before exiting
    #             self.update_campaign_logging(None)
    #             return
    #
    #         # Re-open base logs with recovered flag
    #         self.open_base_logs(campaign_save_name, self.campaign_location, is_recovered=True)
    #
    #         # Re-open campaign log
    #         os.chmod(self.campaign_location + "campaign_log.txt", S_IWUSR | S_IREAD)
    #         self.campaign_log = open(self.campaign_location + "campaign_log.txt", "a+")
    #         self.logSignal.emit("Server", "Campaign '%s' recovered" % campaign_save_name)
    #         self.campaign_log.write("Campaign %s recovered during new server connection\n" % campaign_save_name)
    #
    #     elif campaign_save_name is not None and configuration_data is not None and avionics_mappings is not None:
    #         # Create new campaign logging stuff
    #         self.campaign_location = Constants.campaign_data_dir + campaign_save_name + "/"
    #
    #         # Create test folder
    #         if not os.path.isdir(self.campaign_location + "tests/"):
    #             os.makedirs(self.campaign_location + "tests/")
    #
    #         # Open base logs
    #         self.server.open_base_logs(campaign_save_name, self.campaign_location, is_recovered=False)
    #
    #         # Open log and write a few things
    #         self.campaign_log = open(self.campaign_location + "campaign_log.txt", "w")
    #         self.campaign_log.write("Campaign started with save name: " + campaign_save_name + "\n")
    #         self.server.logSignal.emit("Server", "Campaign '%s' started" % campaign_save_name)
    #
    #         # Write configuration to file
    #         with open(self.campaign_location + "configuration.json", "w") as write_file:
    #             json.dump(configuration_data, write_file, indent="\t")
    #             os.chmod(write_file.name, S_IREAD | S_IRGRP | S_IROTH)
    #
    #         # Write avionics mappings to file
    #         with open(self.campaign_location + "avionicsMappings.csv", "w") as write_file:
    #             write_file.write("Channel,Name\n")
    #             for key in avionics_mappings:
    #                 if key != "Boards":  # currently don't list the boards the user has added
    #                     write_file.write(avionics_mappings[key][1] + "," + avionics_mappings[key][
    #                         0] + "\n")  # key is not useful, first index is name, second is channel
    #             os.chmod(write_file.name, S_IREAD | S_IRGRP | S_IROTH)
    #
    #     else:
    #         print(colored("WARNING: Got a call to update_campaign_logging() that should not occur"), 'red')
    #         self.server.statusBarMessageSignal.emit("Logging command failed. See terminal", True)
    #         # Restart logging
    #         self.update_campaign_logging(None)

    def openCampaignLog(self, isRecovered: bool = False):

        if isRecovered:
            self.campaign_log = open(self.campaign_location + "campaign_log.txt", "a+")

        else:
            # Create test folder
            if not os.path.isdir(self.campaign_location + "tests/"):
                os.makedirs(self.campaign_location + "tests/")

            self.campaign_log = open(self.campaign_location + "campaign_log.txt", "w")
            self.campaign_log.write("Campaign started with save name: " + self.saveName + "\n")

            # Write configuration to file
            with open(self.campaign_location + "configuration.json", "w") as write_file:
                json.dump(self.configurationData, write_file, indent="\t")
                os.chmod(write_file.name, S_IREAD | S_IRGRP | S_IROTH)

            # Write avionics mappings to file
            with open(self.campaign_location + "avionicsMappings.csv", "w") as write_file:
                write_file.write("Channel,Name\n")
                for key in self.avionicsMappings:
                    if key != "Boards":  # currently don't list the boards the user has added
                        write_file.write(self.avionicsMappings[key][1] + "," + self.avionicsMappings[key][
                            0] + "\n")  # key is not useful, first index is name, second is channel
                os.chmod(write_file.name, S_IREAD | S_IRGRP | S_IROTH)

    def startCampaign(self, title: str, configurationData: dict, avionicsMappings: dict):
        if self.isActive:
            print("Campaign already active")
            return
        self.configurationData = configurationData
        self.avionicsMappings = avionicsMappings
        self.isActive = True
        self.title = title
        self.startDateTime = QDateTime.currentDateTime()
        self.CET = 0
        self.startDateTime = QDateTime.currentDateTime()
        self.saveName = self.startDateTime.date().toString("yyyy-MM-dd") + "-T" + self.startDateTime.time().toString(
            "hhmmss") + "__" + self.title.replace(" ", "_")
        self.campaign_location = Constants.campaign_data_dir + self.saveName + "_2/"
        self.server.open_base_logs(self.title, self.campaign_location)
        self.openCampaignLog()

        self.writeToCampaignLog("CET-" + self.CETasString(), "LOG", "Campaign '" + self.title + "' Started")

        self.backgroundThread.start()

    def writeToCampaignLog(self, CET, type_, message):
        self.campaign_log.write(CET + " | " + type_ + " | " + message + "\n")

    def endCampaign(self):

        self.writeToCampaignLog(self.CETasString(), "LOG", "Campaign '" + self.title + "' ended")

        self.isActive = False
        self.CET = None
        self.title = None
        self.startDateTime = None
        self.saveName = None

        self.closeLogs()

    def getCampaignDictionary(self):

        dict_ = {"title_label": self.title, "start_time": self.startDateTime, "test_dict": self.test_dict}

        return dict_

    def closeLogs(self):

        if self.campaign_log is not None and not self.campaign_log.closed:
            self.campaign_log.close()
            self.campaign_location = None
            os.chmod(self.campaign_log.name, S_IREAD | S_IRGRP | S_IROTH)
            self.campaign_log = None

    def closeTestLog(self):

        if self.testLog is not None and not self.testLog.closed:
            self.testLog.close()
            os.chmod(self.testLog.name, S_IREAD | S_IRGRP | S_IROTH)
            self.testLog = None

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




