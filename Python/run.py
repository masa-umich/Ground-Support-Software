from PyQt5.QtCore import *

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


class Campaign(QObject):
    """
    Class that holds all the functions for a new campaign
    """

    # HMM: We only want one instance of this class ever so do we make it a Singleton?!
    # TODO: Currently the Gui will have to be closed and reopened to allow for a new run

    # Signals for this class
    campaignStartSignal = pyqtSignal()
    campaignEndSignal = pyqtSignal()
    updateCETSignal = pyqtSignal(int)
    testStartSignal = pyqtSignal(str)
    testEndSignal = pyqtSignal()

    def __init__(self, gui):
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
        self.gui = gui
        self.title = None
        self.startDateTime = None
        self.CET = None
        self.saveName = None
        self.is_active = False
        self.client = None
        self.numTests = 0
        self.isTestActive = False
        self.currentTestName = None  # not reset back to none after test, holds previous test name till new test created
        self.testDict = {}

    def startRun(self, title: str):
        """
        Start the run, this just populates the pre-initialized variables
        :param title: the title for this test
        :return:
        """
        self.title = title
        self.startDateTime = QDateTime.currentDateTime()
        self.CET = 0
        # ISO 8601 format
        self.saveName = self.startDateTime.date().toString("yyyy-MM-dd") + "-T" + self.startDateTime.time().toString("hhmmss") + "__" + self.title.replace(" ", "_")
        if self.client:
            self.client.command(6, [str(self.saveName), self.gui.controlsWindow.centralWidget.controlsWidget.generateConfigurationSaveData(), self.gui.controlsWindow.centralWidget.controlsWidget.generateSensorMappingsToSend()])
        self.is_active = True
        self.campaignStartSignal.emit()

    def endRun(self):
        """
        End the current run
        """
        # Want to update CET one last time to get final CET before run ends
        self.updateCET()

        if self.isTestActive:
            self.endTest()  # end any tests that need to be

        self.campaignEndSignal.emit()
        if self.client:
            self.client.command(6, None)
        self.is_active = False
        self.CET = None

    def startTest(self, name: str):
        self.isTestActive = True
        self.currentTestName = name
        self.updateCET()
        self.numTests += 1
        self.testDict[name] = {"CET": self.CET, "Test Num": self.numTests}
        self.testStartSignal.emit(name)

    def endTest(self):
        """
        End the current test. All the button updating is handeled by the main window. This function is also called
        by the main window
        """
        self.isTestActive = False
        self.updateCET()
        self.testDict[self.currentTestName]["Duration"] = self.CET - self.testDict[self.currentTestName]["CET"]
        self.testEndSignal.emit()

        print(self.testDict)

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




