import csv
from os import path

import time

from party import PartyParrot
from s2Interface import S2_Interface
import queue

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class ReplayServerDialog(QDialog):

    def __init__(self, gui):
        super().__init__()

        self.gui = gui
        self.replay_server = ReplayServerWindow(self, self.gui)
        self.setWindowTitle("Replay Server Handler")
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.replay_server)
        self.setLayout(self.layout)
        self.setMinimumSize(800, 600)
        base_size = 500
        AR = 1.5  # H/W
        self.setFixedWidth(int(AR * base_size))
        self.setFixedHeight(int(base_size))


class ReplayServerWindow(QMainWindow):

    def __init__(self, dialog, gui):
        """Initializes window

        """
        super().__init__()
        # window top-level layout
        self.dialog = dialog
        self.gui = gui
        self.setWindowTitle("Replay Server")
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.grid_layout = QGridLayout()
        self.widget.setLayout(self.grid_layout)
        self.load_file_name = None
        self.is_replaying = False

        self.counter = 0
        #
        # self.select_file_button = QPushButton("Select Run File")
        # self.select_file_button.clicked.connect(self.openFileDialog)
        # self.select_file_button.setFocusPolicy(Qt.NoFocus)
        #
        # self.load_file_name_edit = QLineEdit()
        # self.load_file_name_edit.setPlaceholderText("Run File Name")
        # font = QFont()
        # font.setPointSize(12 * self.gui.font_scale_ratio)
        # self.load_file_name_edit.setFont(font)
        # self.load_file_name_edit.editingFinished.connect(self.loadFileNameLineEditFinished)
        # self.load_file_name_edit.textEdited.connect(self.loadFileNameLineEdited)
        #
        # self.load_file_button = QPushButton("Load Run File")
        # self.load_file_button.clicked.connect(self.loadRunFile)
        # self.load_file_button.setFocusPolicy(Qt.NoFocus)
        #
        # self.self.grid_layout.addWidget(self.select_file_button, 0 , 0)
        # self.self.grid_layout.addWidget(self.load_file_name_edit, 0, 1)
        # self.self.grid_layout.addWidget(self.load_file_button, 0, 2)

        # initialize parser
        self.interface = S2_Interface()
        self.num_items = len(self.interface.channels)

        self.log_queue = queue.Queue()

        # server log
        tab = QTabWidget()

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        packet_widget = QWidget()
        packet_layout = QHBoxLayout()
        packet_widget.setLayout(packet_layout)

        self.data_box = QTextEdit()
        self.data_box.setReadOnly(True)
        self.data_box.setLineWrapMode(QTextEdit.NoWrap)

        # telemetry table
        self.data_table = QTableWidget()
        self.data_table.setRowCount(self.num_items)
        self.data_table.setColumnCount(3)
        header = self.data_table.horizontalHeader()
        # header.setStretchLastSection(True)
        self.data_table.setHorizontalHeaderLabels(["Channel", "Value", "Unit"])
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        for n in range(self.num_items):
            self.data_table.setItem(
                n, 0, QTableWidgetItem(self.interface.channels[n]))
            self.data_table.setItem(n, 2, QTableWidgetItem(
                self.interface.units[self.interface.channels[n]]))

        packet_layout.addWidget(self.data_box)
        packet_layout.addWidget(self.data_table)

        # tabs
        tab.addTab(self.log_box, "Replayed Server Log")
        tab.addTab(packet_widget, "Replayed Packet Log")
        # top_layout.addWidget(tab, 2, 0) # no parrot
        self.grid_layout.addWidget(tab, 2, 0, 1, 2)

        # please ask Alex before reenabling, need to add circular buffer
        #self.send_to_log(self.data_box, "Packet log disabled")

        # file_load box (add to self.grid_layout)
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
        #self.load_file_name_edit.editingFinished.connect(self.loadFileNameLineEditFinished)
        self.load_file_name_edit.textEdited.connect(self.loadFileNameLineEdited)

        self.load_file_button = QPushButton("Load Run File")
        self.load_file_button.clicked.connect(self.loadRunFile)
        self.load_file_button.setFocusPolicy(Qt.NoFocus)

        file_load_layout.addWidget(self.select_file_button, 0 , 0)
        file_load_layout.addWidget(self.load_file_name_edit, 0, 1)
        file_load_layout.addWidget(self.load_file_button, 0, 2)

        # heartbeat indicator
        self.party_parrot = PartyParrot()
        self.party_parrot.setFixedSize(60, 60)
        self.grid_layout.addWidget(self.party_parrot, 0, 1)

        # populate port box
        #self.scan()

        # commander status
        command_box = QGroupBox("Command Status")
        # self.grid_layout.addWidget(command_box, 1, 0) #no parrot
        self.grid_layout.addWidget(command_box, 1, 0, 1, 2)
        command_layout = QGridLayout()
        command_box.setLayout(command_layout)
        self.commander_label = QLabel("Commander: None")
        command_layout.addWidget(self.commander_label, 0, 0, 0, 4)
        override_button = QPushButton("Override")
        #override_button.clicked.connect(self.override_commander)
        command_layout.addWidget(override_button, 0, 4)

        self.thread = ReplayServerBackgroundThread(self)

        self.thread.parsed.connect(self.updateTable)


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

        self.party_parrot.step()

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
            self.load_file_name = fileName
            self.load_file_name_edit.setText(fileName)
            self.load_file_name_edit.setStyleSheet("")

    def loadRunFile(self):
        #print("oorah")
        f = open(self.load_file_name, 'r', newline='')
        self.reader = csv.reader(f)
        self.thread.start()
        self.is_replaying = True

        header = next(self.reader)

        header = header[1:-1]

        print(header)

        self.header_len = len(header)
        self.units = {}
        self.data_packet_dict = {}

        self.header_items = [''] * self.header_len

        for i,header_itm in enumerate(header):
            split_itm = header_itm.split()

            name = split_itm[0]
            if len(split_itm) is 2:
                unit = split_itm[1]
            else:
                unit = "(ul)"
            self.header_items[i] = name
            self.units[name] = unit

        junk = next(self.reader)

        print(self.header_items)
        print(self.units)

    def updateTable(self, dict):

        for i, data_item in enumerate(self.header_items):
            self.data_table.setItem(i, 1, QTableWidgetItem(str(dict[self.header_items[i]])))

    def readRunFile(self):
        row1 = next(self.reader)
        self.counter = self.counter + 1
        #print(row1)
        self.parseData(data_row= row1[0:-1])
            # print([n, key, dataframe[key]])


        # self.data_table.update()
        # self.update()
        # self.dialog.update()

    def parseData(self, data_row):

        for i, data_item in enumerate(data_row):
            #print(data_item)
            num_data = round(float(data_item), 1)
            self.data_packet_dict[self.header_items[i]] = num_data
            self.data_table.setItem(1, 1, QTableWidgetItem(str(num_data)))

    def loadFileNameLineEdited(self):

        file_path = self.load_file_name_edit.text()
        if path.exists(file_path):
            self.load_file_name_edit.setStyleSheet("")
            self.load_file_name = file_path
        else:
            self.load_file_name = None
            self.is_replaying = False
            if file_path is not "":
                self.load_file_name_edit.setStyleSheet("color: red;")
            else:
                self.load_file_name_edit.setStyleSheet("")


class ReplayServerBackgroundThread(QThread):
    """
    Class that handles background threading for the run class, this is to prevent the GUI from hanging
    """

    parsed = pyqtSignal(object)

    def __init__(self, replayServer: ReplayServerWindow):
        """
        Initializer
        :param run: The run instance that is currently active
        """
        super().__init__()
        self.replay_server = replayServer

    def run(self):
        """
        This is the function that is constantly running in the background
        """
        print("test")
        # While the run is active keep the thread alive, will cleanly exit when run stops
        while self.replay_server.is_replaying:
            # Update the MET every second, this can be increased but seems unnecessary
            self.readRunFile()
            #self.replay_server.party_parrot.step()
            time.sleep(.1)


    def readRunFile(self):
        row1 = next(self.replay_server.reader)
        # print(row1)
        self.parseData(data_row=row1[1:-1])
        # print([n, key, dataframe[key]])

        # self.data_table.update()
        # self.update()
        # self.dialog.update()

    def parseData(self, data_row):

        dict = {}
        for i, data_item in enumerate(data_row):
            # print(data_item)
            num_data = round(float(data_item), 1)
            dict[self.replay_server.header_items[i]] = num_data

        self.parsed.emit(dict)

