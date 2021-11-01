from PyQt5.QtCore import *

import time

"""
This file contains the class and functions to handle the 'run' or test being conducted
"""


class Campaign:
    pass


class Run(QObject):  #
    """
    Class that holds all the functions for a new run
    """

    # HMM: We only want one instance of this class ever so do we make it a Singleton?!
    # TODO: Currently the Gui will have to be closed and reopened to allow for a new run

    # Signals for this class
    runStartSignal = pyqtSignal()
    runEndSignal = pyqtSignal()
    updateMETSignal = pyqtSignal(int)

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
        :var MET: The mission elapsed time for this run/ test in milliseconds
        :var saveName: The name that will be used to title files
        """
        super().__init__()

        # All of these are set to none to make sure if someone access before it is created it fails
        self.title = None
        self.is_active = False  # Use this to check if the run is running
        self.startDateTime = None
        self.MET = None
        self.saveName = None
        self.boards = None  # TODO: This really should not go here because it is a part of the configuration
        self.thread = None
        self.client = None

    def startRun(self, title: str):
        """
        Start the run, this just populates the pre-initialized variables
        :param title: the title for this test
        :return:
        """
        self.title = title

        if self.client:
            self.client.command(6, str(title)) #TODO: input validation 

        self.is_active = True
        self.startDateTime = QDateTime.currentDateTime()
        self.MET = 0
        self.saveName = self.startDateTime.date().toString("yyyy-MM-dd") + "-T" + \
                                self.startDateTime.time().toString("hhmm") + "__" + self.title.replace(" ", "_")
        self.thread = RunBackgroundThread(self)
        self.thread.start()

        self.runStartSignal.emit()

    def endRun(self):
        """
        End the current run
        """
        # Want to update MET one last time to get final MET before run ends
        self.updateMET()
        self.is_active = False
        self.runEndSignal.emit()
        if self.client:
            self.client.command(6, None)

    def updateMET(self):
        """
        This function updates the MET time for the run. Should be called whenever the MET being accurate is critical
        """
        # Have to double check this here because thread is still in loop when run ends and one last MET update occurs
        if self.is_active:
            # Set the MET, note the msecTo function returns negative for times in the past
            self.MET = -1 * QDateTime.currentDateTime().msecsTo(self.startDateTime)
            # Emit the signal that will allow other parts of the GUI to update with this data
            self.updateMETSignal.emit(self.MET)
    
    def setClient(self, client):
        self.client = client


class RunBackgroundThread(QThread):
    """
    Class that handles background threading for the run class, this is to prevent the GUI from hanging
    """

    def __init__(self, run):
        """
        Initializer
        :param run: The run instance that is currently active
        """
        super().__init__()
        self.run = run

    def run(self):
        """
        This is the function that is constantly running in the background
        """

        # While the run is active keep the thread alive, will cleanly exit when run stops
        while self.run.is_active:
            # Update the MET every second, this can be increased but seems unnecessary
            time.sleep(1)
            self.run.updateMET()
