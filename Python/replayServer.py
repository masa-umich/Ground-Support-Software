import csv
from os import path

import time
import socket
import threading
import pickle
import traceback

from party import PartyParrot
from constants import Constants
from indicatorLightWidget import IndicatorLightWidget
from overrides import overrides
import queue

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


threading.stack_size(134217728)


class ReplayServerDialog(QDialog):
    """
    Class that simply launches a dialog and populates it with underlying window
    """

    def __init__(self, gui):
        super().__init__()

        self.gui = gui
        self.setWindowTitle("Replay Server")
        self.replay_server = ReplayServerWindow(self, self.gui)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.replay_server)
        self.setLayout(self.layout)
        self.setMinimumSize(800, 500)
        base_size = 500
        AR = 1.5  # H/W
        self.setFixedWidth(int(AR * base_size))


class ReplayServerWindow(QMainWindow):
    """
    Replay Server Window, holds everything to show the graphsics
    """

    def __init__(self, dialog, gui):
        """Initializes window

        """
        super().__init__()
        # window top-level layout
        # Window layout is as follows, Central Widget -> Grid Layout -> Groupbox -> Individual Widgets
        self.dialog = dialog
        self.gui = gui
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.grid_layout = QGridLayout()
        self.widget.setLayout(self.grid_layout)

        # Connection port and host
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 6968

        # For the user uk
        self.dialog.setWindowTitle("Replay Server %s:%s" % (self.host, self.port))

        # State vars keeping track of playback controls
        self.csv_thread_active = False
        self.is_playing = False
        self.fast_forward_multiplier = 1

        # Data to be populated and shown
        self.data_units = {}
        self.data_dict = {}
        self.header_items = None

        # Gui shutdown signal connect
        self.gui.app.aboutToQuit.connect(lambda: self.stopPlayback(0))

        # Thread that holds functionality for reading csv, unpacking data
        self.csv_thread = ReplayServerBackgroundCSVThread(self)

        # CANNOT update gui from thread, must use signals to keep all updates in main thread
        self.csv_thread.parsed.connect(self.updateStateFromPacket)
        self.csv_thread.EOF_reached.connect(self.stopPlayback)
        self.csv_thread.file_load.connect(self.loadRunFileData)

        # Setup Status bar
        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.monospace_font)
        font.setPointSizeF(14 * self.gui.font_scale_ratio)
        self.statusBar().setFont(font)
        self.statusBar().showMessage("Dialog Launched")

        # Idk what this does
        self.log_queue = queue.Queue()

        # Setup tab widget holding server log view and data table view
        tab = QTabWidget()

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        packet_widget = QWidget()
        packet_layout = QHBoxLayout()
        packet_widget.setLayout(packet_layout)

        self.data_box = QTextEdit()
        self.data_box.setReadOnly(True)
        self.data_box.setLineWrapMode(QTextEdit.NoWrap)

        # Replayed Data View, 3 cols, unknown # of rows
        self.data_table = QTableWidget()
        self.data_table.setRowCount(1)
        self.data_table.setColumnCount(3)
        header = self.data_table.horizontalHeader()
        # header.setStretchLastSection(True)
        self.data_table.setHorizontalHeaderLabels(["Channel", "Value", "Unit"])
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        Vheader = self.data_table.verticalHeader()
        Vheader.setDefaultAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        packet_layout.addWidget(self.data_box)
        packet_layout.addWidget(self.data_table)

        # Tabs user can pic
        tab.addTab(self.log_box, "Replayed Server Log")
        tab.addTab(packet_widget, "Replayed Packet Log")
        self.grid_layout.addWidget(tab, 3, 0, 1, 2)

        # Load file controls
        file_load_groupbox = QGroupBox("Load Run From Save")
        self.grid_layout.addWidget(file_load_groupbox, 0, 0)
        file_load_layout = QGridLayout()
        file_load_groupbox.setLayout(file_load_layout)

        self.select_file_button = QPushButton("Select Run File")
        self.select_file_button.clicked.connect(self.openFileDialog)
        self.select_file_button.setFocusPolicy(Qt.NoFocus)

        self.load_file_name_edit = QLineEdit()
        self.load_file_name_edit.setPlaceholderText("Run File Name")
        font = QFont()
        font.setPointSize(12 * self.gui.font_scale_ratio)
        self.load_file_name_edit.setFont(font)
        self.load_file_name_edit.textEdited.connect(self.loadFileNameLineEdited)

        self.load_file_button = QPushButton("Load Run File")
        self.load_file_button.clicked.connect(self.csv_thread.loadRunFile)
        self.load_file_button.setFocusPolicy(Qt.NoFocus)

        file_load_layout.addWidget(self.select_file_button, 0 , 0)
        file_load_layout.addWidget(self.load_file_name_edit, 0, 1)
        file_load_layout.addWidget(self.load_file_button, 0, 2)

        # Party parrot heartbeat indicator
        self.party_parrot = PartyParrot()
        self.party_parrot.setFixedSize(60, 60)
        self.grid_layout.addWidget(self.party_parrot, 0, 1)

        # populate port box
        #self.scan()

        # Playback Controls
        command_box = QGroupBox("Playback Controls")
        self.grid_layout.addWidget(command_box, 2, 0, 1, 2)
        command_layout = QGridLayout()
        command_box.setLayout(command_layout)

        # TODO: Make this graphical uk
        rewind_button = QPushButton()
        rewind_button.setText("Rewind :(")
        rewind_button.setFocusPolicy(Qt.NoFocus)
        rewind_button.setDisabled(True)
        # This is going to be a fucking nightmare

        self.play_button = QPushButton()
        self.play_button.setText("Play")
        self.play_button.pressed.connect(self.playPauseButtonPressed)
        self.play_button.setFocusPolicy(Qt.NoFocus)
        self.play_button.setDisabled(True)

        self.fast_forward_button = QPushButton()
        self.fast_forward_button.setText("Fast Forward")
        self.fast_forward_button.pressed.connect(self.fastForwardButtonPressed)
        self.fast_forward_button.setDisabled(True)
        self.fast_forward_button.setFocusPolicy(Qt.NoFocus)

        stop_button = QPushButton()
        stop_button.setText("Stop")
        stop_button.pressed.connect(lambda: self.stopPlayback(0))
        stop_button.setFocusPolicy(Qt.NoFocus)

        command_layout.addWidget(rewind_button, 0, 0)
        command_layout.addWidget(self.play_button, 0, 1)
        command_layout.addWidget(self.fast_forward_button, 0, 2)
        command_layout.addWidget(stop_button, 0, 3)

        # commander status
        server_connection_box = QGroupBox("Connection")
        # top_layout.addWidget(command_box, 1, 0) #no parrot
        self.grid_layout.addWidget(server_connection_box, 1, 0)
        server_connection_layout = QGridLayout()
        server_connection_box.setLayout(server_connection_layout)
        self.client_label = QLabel("Client Connection: None")
        server_connection_layout.addWidget(self.client_label, 0, 0, 0, 4)

        self.connection_indicator = IndicatorLightWidget(self, "", 16, "Red", Hbuffer=26, Wbuffer=15)
        self.connection_indicator.setToolTip("Connections Disabled, No file loaded")
        self.grid_layout.addWidget(self.connection_indicator, 1, 1)

        # start server connection thread
        # waits for clients and then creates a thread for each connection
        #self.t = threading.Thread(target=self.server_handler, daemon=True)
        #self.t.start()

        # # menu bar
        # main_menu = self.menuBar()
        # main_menu.setNativeMenuBar(True)
        # file_menu = main_menu.addMenu('&File')
        #
        # # quit application menu item
        # quit_action = QAction("&Quit", file_menu)
        # quit_action.setShortcut("Ctrl+Q")
        # quit_action.triggered.connect(self.exit)
        # file_menu.addAction(quit_action)

        self.party_parrot.setConfused()

        self.server_handler_thread = None

        self.server_socket = None
        self.client_socket = None

    def serverHandler(self):

        # Initialize socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # This allows instant restart from SIGKILL
        self.server_socket.bind((self.host, self.port))

        self.server_socket.listen(5)

        # create connection
        # establish connection with client
        while True:
            try:
                cli, addr = self.server_socket.accept()
            except ConnectionAbortedError:
                # When we pull the plug on the server this is triggered
                break

            self.client_label.setText("Client Connection: " + addr[0])
            self.connection_indicator.setIndicatorColor("Green")
            self.connection_indicator.setToolTip("Client Connection: " + addr[0])
            self.update()
            # create thread to handle client
            client_thread = threading.Thread(target=self.clientHandler,
                                              args=(cli, addr), daemon=True)
            client_thread.start()

    def clientHandler(self, client_socket: socket.socket, server_addr: str):

        self.client_socket = client_socket
        while self.client_socket is not None:
            msg = self.client_socket.recv(2048)

            if msg == b'':
                # remote connection closed
                break
            else:
                command = pickle.loads(msg)
                if command["command"] == 0:  # do nothing
                    pass
                elif command["command"] == 4:  # close connection
                    break
                else:
                    print("Unrecognized Command Sent to Replay Server")

                self.data_dict["commander"] = "ReplayServer"
                data = pickle.dumps(self.data_dict)
                self.client_socket.sendall(data)

        # Close the socket when the loop breaks
        self.client_socket.close()

        # Only want to make this yellow if the file is still loaded, otherwise will be dealt with elsewhere
        if self.csv_thread_active:
            self.client_label.setText("Client Connection: None")
            self.connection_indicator.setIndicatorColor("Yellow")
            self.connection_indicator.setToolTip("Waiting for connection")
            self.update()

        self.client_socket = None
        self.server_handler_thread.join()

    @pyqtSlot(int, object, object)
    def loadRunFileData(self, exit_code: int, header_items, units):
        """
        This function is connected to a signal emitted from the thread when the thread completed loading the run file
        data. This function takes that data and updates the internal variables and populates the dialog window
        :param exit_code: used to pass data if the file load was successful
        :param header_items: a list of strings containing the names of each col in the csv
        :param units: a dictionary of units. The above header items are the key
        :return:
        """

        exit_code = exit_code

        if exit_code == -1:
            self.sendStatusBarMessage("No file specified! File cannot be loaded", is_error=True)
        else:
            # Activate thread, we start the thread here, but will not populate data till is_playing is true
            self.csv_thread_active = True
            self.sendStatusBarMessage("File loaded")
            self.csv_thread.start()

            # Start server thread to allow incoming connections
            self.server_handler_thread = threading.Thread(target=self.serverHandler, daemon=True)
            self.server_handler_thread.start()

            # Update connection indicator
            self.connection_indicator.setIndicatorColor("Yellow")
            self.connection_indicator.setToolTip("Waiting for connection")

            self.data_table.setRowCount(1)  # Do not change this, idk why but it makes it run way faster and not hang

            # Populate variables
            self.header_items = header_items
            self.data_units = units

            # Populate the data table with the loaded variables and units
            self.data_table.clearContents()
            self.data_table.setRowCount(len(header_items))
            for i, header_item in enumerate(header_items):
                    self.data_table.setItem(i, 0, QTableWidgetItem(header_item))
                    self.data_table.setItem(i, 2, QTableWidgetItem(self.data_units[header_item]))

            # Disable and enable some buttons to prevent user from changing file mid playback
            self.load_file_button.setDisabled(True)
            self.load_file_name_edit.setDisabled(True)
            self.select_file_button.setDisabled(True)

            self.play_button.setDisabled(False)
            self.fast_forward_button.setDisabled(False)

            self.update()

    @pyqtSlot(int)
    def stopPlayback(self, exit_code: int = 0):
        """
        This is a slot for signals that shutdown the gui, and when thread EOF but also just connected to buttons.
        Will stop all playback, end the thread, and get everything ready for a new file to be loaded if needed
        :param exit_code: used to pass data if playback needs to stop because of an error (like EOF)
        """

        # Shutdown thread
        self.csv_thread_active = False
        self.is_playing = False
        self.csv_thread.shutdownThread()

        # Close the sockets

        # Send command to let client know to terminate it
        if self.client_socket is not None:
            dict_ = {"terminate": True}
            data = pickle.dumps(dict_)
            self.client_socket.sendall(data)

        if self.server_socket is not None:
            self.server_socket.close()
            self.server_socket = None

        # Reset the indicator
        self.connection_indicator.setIndicatorColor("Red")
        self.connection_indicator.setToolTip("Connections Disabled, No file loaded")
        self.update()

        self.client_label.setText("Client Connection: None")

        # Reset some vars
        self.fast_forward_multiplier = 1
        self.fast_forward_button.setText("Fast Forward")
        self.play_button.setText("Play")

        # Disable and re-enable some buttons
        self.load_file_button.setDisabled(False)
        self.load_file_name_edit.setDisabled(False)
        self.select_file_button.setDisabled(False)

        self.play_button.setDisabled(True)
        self.fast_forward_button.setDisabled(True)

        if exit_code == 0:
            self.sendStatusBarMessage("Playback Stopped")
        elif exit_code == -1:
            self.sendStatusBarMessage("End of file reached", is_error=True)

        self.party_parrot.setConfused()

    def playPauseButtonPressed(self):
        """
        When the play buttons is pressed, toggle between play and paused
        """

        if self.is_playing:
            self.is_playing = False
            self.play_button.setText("Play")
            self.sendStatusBarMessage("Paused Playing")
            self.fast_forward_multiplier = 1
            self.fast_forward_button.setText("Fast Forward")
            self.party_parrot.setConfused()
        else:
            self.is_playing = True
            self.play_button.setText("Pause")
            self.sendStatusBarMessage("Started Playing")

    def fastForwardButtonPressed(self):
        """
        When the fast forward button is pressed, speed up the playback
        """

        # Make sure playing is actually active when fast forward is pressed
        if not self.is_playing:
            self.is_playing = True
            self.play_button.setText("Pause")

        # If the multiplier is not maxed out increase the speed 2x
        if self.fast_forward_multiplier < 32:
            self.fast_forward_multiplier = self.fast_forward_multiplier * 2
        else:
            self.fast_forward_multiplier = 2

        # Update the label
        self.fast_forward_button.setText("Fast Forward (" + str(self.fast_forward_multiplier) + "x)")
        self.sendStatusBarMessage("Fastforward " + str(self.fast_forward_multiplier) + "x")

    def send_to_log(self, textedit: QTextEdit, text: str, timestamp: bool = True):
        """Sends a message to a log.

        Args:
            textedit (QTextEdit): Text box to send to
            text (str): Text to write
            timestamp (bool): add timestamp
        """
        self.log_queue.put([textedit, text, timestamp])

    def openFileDialog(self):
        """
        Pulls up open file dialog, loads data from selected file
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Run File", "/Users/jt/Desktop/Michigan/MASA/Avionics/Code/gui/Python/data/20210425181635_test1-attempt2_data_log.csv", "CSV Files (*.csv)", options=options)
        if fileName:
            self.updateRunFilePath(fileName)

    @pyqtSlot(object)
    def updateStateFromPacket(self, dict_: dict):
        """
        Update the state of the dialog from the received dictionary packet. Connected the thread parsed signal
        :param dict_: dictionary with keys of header items and values the parsed value of the csv
        """
        self.party_parrot.step()
        self.data_dict = dict_
        for i, data_item in enumerate(self.header_items):
            self.data_table.setItem(i, 1, QTableWidgetItem(str(round(dict_[self.header_items[i]],1))))

    def loadFileNameLineEdited(self):
        """
        Called when the line edit is edited, seets the name and color
        """

        file_path = self.load_file_name_edit.text()
        if path.exists(file_path):
            self.updateRunFilePath(file_path)
        else:
            self.csv_thread.setRunFilePath(None)
            if file_path is not "":
                self.load_file_name_edit.setStyleSheet("color: red;")
            else:
                self.load_file_name_edit.setStyleSheet("")

    def updateRunFilePath(self, filePath):
        """
        Helper function that sets the file path to the CSV
        :param filePath: file path to csv file
        """
        self.load_file_name_edit.setStyleSheet("")
        self.load_file_name_edit.setText(filePath)
        self.csv_thread.setRunFilePath(filePath)
        self.sendStatusBarMessage("File path successfully updated")

    def sendStatusBarMessage(self, message: str, is_error: bool = False):
        """
        Helper function that sends a message to the status bar of the dialog
        :param message: message to display
        :param is_error: flag if the message should display as an error
        """
        if is_error:
            self.statusBar().setStyleSheet("color: red;")
            self.statusBar().showMessage(message)
        else:
            self.statusBar().setStyleSheet("")
            self.statusBar().showMessage(message)

    @overrides
    def update(self):
        """
        Overrides update function to make sure some sub-widgets get updated
        """
        super().update()

        self.connection_indicator.update()


class ReplayServerBackgroundCSVThread(QThread):
    """
    Class that handles csv background threading for the run class, this is to prevent the GUI from hanging
    """

    file_load = pyqtSignal(int, object, object)  # Emitted when the file is loaded
    parsed = pyqtSignal(object)  # Emitted when a row of the file is parsed
    EOF_reached = pyqtSignal(int)  # Emitted when the end of file is reached

    def __init__(self, replayServer: ReplayServerWindow):
        """
        Initializer
        :param replayServer: The replayServer instance that is currently active
        """
        super().__init__()
        self.gui = replayServer.gui
        self.replay_server = replayServer
        self.run_file_path = None
        self.csv_reader = None
        self.run_file = None

        self.default_playback_speed = 0.1
        self.paused_sleep_duration = .1

    def run(self):
        """
        This is the function that is constantly running in the background
        """
        # While the run is active keep the thread alive, will cleanly exit when run stops
        while self.replay_server.csv_thread_active:

            if self.replay_server.is_playing:
                # Update the MET every second, this can be increased but seems unnecessary
                self.readRunFile()
                time.sleep(self.default_playback_speed / self.replay_server.fast_forward_multiplier)
            else:
                time.sleep(self.paused_sleep_duration)

    def shutdownThread(self):
        """
        Shutdown the thread
        """
        # Just close the file for now
        if self.run_file is not None:
            self.run_file.close()

    def loadRunFile(self):
        """
        Open the run file, takes the header row parses for names and units
        """
        # Make sure a file is loaded, otherwise gui will throw error
        if self.run_file_path is None:
            self.file_load.emit(-1, None, None)  # Emit just the error code
            return

        # Open the run file and get the csv file reader
        self.run_file = open(self.run_file_path, 'r')
        self.csv_reader = csv.reader(self.run_file)

        # Don't want the server timestamp, and garbage last entry
        header = next(self.csv_reader)
        header = header[0:-1]

        header_len = len(header)
        units = {}

        # For every item in the header, get the name and the units
        header_items = [''] * header_len
        for i, header_itm in enumerate(header):
            split_itm = header_itm.split()

            name = split_itm[0]
            if len(split_itm) is 2:
                unit = split_itm[1]
            else:
                unit = "(ul)"
            header_items[i] = name
            units[name] = unit

        # Random blank line
        _ = next(self.csv_reader)

        # Emit the loaded data
        self.file_load.emit(0, header_items, units)

        # Populate first value
        self.readRunFile()

    def readRunFile(self):
        """
        Reads the next row of the run file
        """
        try:
            # Read the next row
            next_raw_row = next(self.csv_reader)
            self.parseData(data_row=next_raw_row[0:-1])  # Have to cut off for same reason mentioned in loadRunFile()
        except StopIteration:
            # Exception caught when EOF is found
            self.shutdownThread()
            self.EOF_reached.emit(-1)  # -1 is the EOF exit code for this

    def parseData(self, data_row):
        """
        Parses the row data (a list), into a dictionary and emit the dict when complete
        :param data_row: list of the row data
        """

        # For every piece of data in in the data_row, take it and stuff it in a dictionary with the headers as keys
        dict = {}
        for i, data_item in enumerate(data_row):
            num_data = float(data_item)
            dict[self.replay_server.header_items[i]] = num_data

        # This emits a signal w/ dictionary that the run can pickup to update the server from the main thread
        self.parsed.emit(dict)

    def setRunFilePath(self, file_path: str):
        """
        Sets the file path the thread should be using
        :param file_path: file path string
        """
        self.run_file_path = file_path