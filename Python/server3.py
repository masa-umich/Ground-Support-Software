from __future__ import annotations  # see https://stackoverflow.com/questions/61544854/from-future-import-annotations

import ctypes
import os
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR
import pickle
import queue
import socket
import sys
import threading
from datetime import datetime
import traceback
import time
import hashlib
import json
from termcolor import colored
from typing import TextIO

from overrides import overrides
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants
from party import PartyParrot
from s2Interface import S2_Interface
from packetLogWidget import PacketLogWidget
import parse_auto

threading.stack_size(134217728)


class ServerGraphics(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Server 3")

        self.central_widget = QWidget()

        self.setCentralWidget(self.central_widget)

        base_size = 700
        AR = 1.4  # H/W
        self.setMinimumSize(int(AR * base_size), int(base_size))

        self.statusBar().setFixedHeight(22)

        self.show()

        self.server = Server()

        # Setup displat
        self.top_grid_layout = QGridLayout()
        self.central_widget.setLayout(self.top_grid_layout)

        self.board_connection_group_box = QGroupBox("Board Serial Connection")
        b_c_group_box_layout = QGridLayout() #b_c = client connection
        self.board_connection_group_box.setLayout(b_c_group_box_layout)

        self.b_c_scan_button = QPushButton("Scan Ports:")
        self.b_c_scan_button.clicked.connect(self.update_b_c_ports_combo)
        self.b_c_scan_button.setFocusPolicy(Qt.NoFocus)
        b_c_group_box_layout.addWidget(self.b_c_scan_button, 0, 0)

        self.b_c_ports_combo_box = QComboBox()
        self.b_c_ports_combo_box.addItems(self.server.scan())
        b_c_group_box_layout.addWidget(self.b_c_ports_combo_box, 0, 1, 0, 2)

        self.b_c_baudrate_label = QLabel("Baudrate:")
        self.b_c_baudrate_label.adjustSize()
        self.b_c_baudrate_label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        b_c_group_box_layout.addWidget(self.b_c_baudrate_label, 0, 3)

        self.b_c_baudrate_combo_box = QComboBox()
        self.b_c_baudrate_combo_box.addItems(["3913043", "115200"])
        b_c_group_box_layout.addWidget(self.b_c_baudrate_combo_box, 0, 4)

        self.b_c_connect_button = QPushButton("Connect")
        self.b_c_connect_button.clicked.connect(lambda: self.server.connect_to_board(
            self.b_c_ports_combo_box.currentText(), int(self.b_c_baudrate_combo_box.currentText())))

        b_c_group_box_layout.addWidget(self.b_c_connect_button, 0, 5)

        self.b_c_packet_label = QLabel("Last Packet Size: 0")
        self.b_c_packet_label.adjustSize()
        self.b_c_packet_label.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        self.b_c_packet_label.setMinimumWidth(200)
        self.b_c_packet_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        b_c_group_box_layout.addWidget(self.b_c_packet_label, 0, 6)

        self.party_parrot = PartyParrot()
        self.party_parrot.setFixedSize(60, 60)
        # b_c_group_box_layout.addWidget(self.party_parrot, 0, 7)
        self.party_parrot.step()

        self.top_grid_layout.addWidget(self.board_connection_group_box, 0, 0)
        self.board_connection_group_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.top_grid_layout.addWidget(self.party_parrot, 0, 2)

        self.commander_group_box = QGroupBox("Commander Status")
        commander_group_box_layout = QGridLayout()
        self.commander_group_box.setLayout(commander_group_box_layout)

        self.top_grid_layout.addWidget(self.commander_group_box, 1, 0, 1, 0)

        self.commander_label = QLabel("Commander UUID: None")
        commander_group_box_layout.addWidget(self.commander_label, 0, 0, 0, 4)

        self.commander_override_button = QPushButton("Override Commander")
        self.commander_override_button.clicked.connect(self.server.override_commander)
        commander_group_box_layout.addWidget(self.commander_override_button, 0, 5, 0, 1)

        self.info_tab_widget = QTabWidget()

        mono_font = QFont()
        mono_font.setStyleStrategy(QFont.PreferAntialias)
        mono_font.setFamily(Constants.monospace_font)

        self.server_log_textedit = QTextEdit()
        self.server_log_textedit.setReadOnly(True)
        self.server_log_textedit.setFont(mono_font)
        self.info_tab_widget.addTab(self.server_log_textedit, "Server Log")

        self.command_log_textedit = QTextEdit()
        self.command_log_textedit.setReadOnly(True)
        self.command_log_textedit.setLineWrapMode(QTextEdit.NoWrap)
        self.command_log_textedit.setFont(mono_font)
        self.info_tab_widget.addTab(self.command_log_textedit, "Board Command Log")

        packet_log_widget = QWidget()
        packet_log_hbox_layout = QHBoxLayout()
        packet_log_widget.setLayout(packet_log_hbox_layout)
        self.packet_log_textedit = QTextEdit("Packet Log disabled until implemented")
        self.packet_log_textedit.setReadOnly(True)

        self.packet_log_table = PacketLogWidget(self.info_tab_widget, self.server.interface, self.server.dataPacketSignal, True)

        #packet_log_hbox_layout.addWidget(self.packet_log_textedit)
        packet_log_hbox_layout.addWidget(self.packet_log_table)

        self.info_tab_widget.addTab(packet_log_widget, "Packet Log")

        commandline_widget = QWidget()
        commandline_grid_layout = QGridLayout()
        commandline_widget.setLayout(commandline_grid_layout)

        self.commandline_line_edit = QLineEdit()
        self.commandline_line_edit.installEventFilter(self)
        self.commandline_line_edit.setPlaceholderText("Command line interface. Type \"help\" for info.")

        self.commandline_local_commands = ["delay", "set_addr", "help", "auto"]
        possible_commands = self.server.get_command_list() + self.commandline_local_commands
        possible_commands = possible_commands + ["help " + x for x in self.server.get_command_list()]
        completer = QCompleter(possible_commands)
        self.commandline_line_edit.setCompleter(completer)
        self.commandline_line_edit.returnPressed.connect(self.processCommandLine)
        commandline_grid_layout.addWidget(self.commandline_line_edit, 0, 0, 1, 4)

        self.commandline_board_dropdown = QComboBox()
        self.commandline_board_dropdown.addItems(Constants.boards)
        commandline_grid_layout.addWidget(self.commandline_board_dropdown, 0, 4)

        self.commandline_textbox = QTextEdit()
        self.commandline_textbox.setReadOnly(True)
        self.commandline_textbox.setFont(mono_font)
        commandline_grid_layout.addWidget(self.commandline_textbox, 1, 0, 1, 0)

        self.info_tab_widget.addTab(commandline_widget, "Command Line")

        self.top_grid_layout.addWidget(self.info_tab_widget, 2, 0, 1, 0)

        self.command_line_history = []
        self.command_line_history_idx = -1

        # Signal connections
        self.server.statusBarMessageSignal.connect(self.setStatusBarMessage)
        self.server.logSignal.connect(self.messageToLog)
        self.server.commanderLabelSignal.connect(self.commander_label.setText)
        self.server.packetSizeLabelSignal.connect(self.b_c_packet_label.setText)
        self.server.partyParrotStepSignal.connect(self.party_parrot.step)

        self.server.delayed_init()

        self.setStatusBarMessage("Startup Complete")

    def update_b_c_ports_combo(self):
        """
        Simply updates the Client Connection groupbox, ports dropdown
        :return: None
        """
        self.b_c_ports_combo_box.clear()
        self.b_c_ports_combo_box.addItems(self.server.scan())

    def exit(self, args):
        """
        Called when the server is closed or exited
        :param args: idk if anything is actually here but I don't care about it
        :return: None
        """
        self.server.exit()

    def setStatusBarMessage(self, text: str, error: bool = False):
        """
        Set text and possible show as error for status bar
        :param text: text to set
        :param error: bool, true for error
        :return: none
        """
        if error:
            self.statusBar().setStyleSheet("background-color: red")
        else:
            self.statusBar().setStyleSheet("border-top :1px solid #4F4F52")

        self.statusBar().showMessage(text)

    def processCommandLine(self):
        """
        Processes command line interface
        :return: None
        """

        commands = self.server.get_command_list()

        # Add and reset history
        self.command_line_history = [self.commandline_line_edit.text()] + self.command_line_history
        self.command_line_history_idx = -1

        # Get inputted command + board address
        cmd_str = self.commandline_line_edit.text().lower().split(" ")
        board_addr = self.server.get_board_address(self.commandline_board_dropdown.currentText())
        cmd = cmd_str[0]
        args = cmd_str[1:]

        # Couple commands to log command. Insert plain text still gets colors.
        self.commandline_textbox.append(Constants.getCurrentTimestamp())

        self.commandline_textbox.setTextColor(QColor(55, 70, 200))

        self.commandline_textbox.insertPlainText(self.commandline_board_dropdown.currentText())

        self.commandline_textbox.setTextColor(QColor(0, 0, 0, 255))

        self.commandline_textbox.insertPlainText(" % ")

        self.commandline_textbox.setTextColor(QColor(140, 30, 140))

        self.commandline_textbox.insertPlainText(cmd + " " + str(args))

        self.commandline_textbox.setTextColor(QColor(0, 0, 0, 255))

        if cmd == "help":
            if len(args) == 0:
                self.commandline_textbox.append(
                    "Enter commands as: <COMMAND> <ARG1> <ARG2> ... <ARGN>\n\nAvailable commands:\n%s\n\nFor more information on a command type: help <COMMAND>\n\nTo run an auto-sequence type: auto <NAME>\nPut your autosequence files in Python/autos/\n" % commands, )
            elif args[0] in (self.commandline_local_commands + commands):
                selected_cmd = args[0]
                cmd_args = self.getCommandLineHelp(selected_cmd)
                #TODO: Improve how this is shown
                self.commandline_textbox.append("Args: arg(format)\n%s" % (cmd_args))
        else:
            self.server.process_command_line(cmd, args, board_addr)

        self.commandline_textbox.scroll(0, 0)  # Not sure why/ how but this scrolls textbox to bottom

        self.commandline_line_edit.clearFocus()
        self.commandline_line_edit.clear()

    def getCommandLineHelp(self, selected_command):
        """
        Shows quick command help from s2 interface
        :param selected_command: command requested for help
        :return: help text for command
        """
        commands = self.server.get_command_list()

        tooltips = {}
        for cmd in commands:

            tip = "%s" % cmd
            cmd_args = self.server.get_command_args(cmd)
            for arg in cmd_args:
                name = arg[0]
                arg_type = arg[1]
                tip += " %s(%s)" % (name, arg_type)
            tooltips[cmd] = tip

        tooltips["delay"] = "delay time(int, milliseconds)"
        tooltips["set_addr"] = "set_addr target_addr(int)"
        tooltips["auto"] = "auto auto_name(str)"

        for local_cmd in self.commandline_local_commands:
            if local_cmd != "help" and local_cmd not in tooltips.keys():
                print(colored("WARNING: No help text defined for local command " + local_cmd, 'red'))

        return tooltips[selected_command]

    @pyqtSlot(str, str)
    def messageToLog(self, log: str, message: str):
        """
        Add message to one of the logs with timemstamp
        :param log: name of log to send too
        :param message: message to add
        :return: None
        """

        if log == "Server":
            self.server_log_textedit.append(Constants.getCurrentTimestamp() + message)
        elif log == "Command":
            self.command_log_textedit.append(Constants.getCurrentTimestamp() + message)
        else:
            print(colored("WARNING: messageToLog() called with '%s' log identifier that does not exist" % log))

    def eventFilter(self, source, event):
        """
        Event filters handles keyboard input, focus events and other things. Here it is used for command line
        :param source: source widget calling this
        :param event: even that occurred
        :return: Return true when event was dealt with, if not the pass to super
        """
        # up and down arrows in command line to see previous commands
        if source is self.commandline_line_edit and event.type() == QEvent.KeyPress:

            # Bound to make sure we are not going to be index out of range
            if event.key() == Qt.Key_Up:
                self.command_line_history_idx += 1
                if self.command_line_history_idx >= len(self.command_line_history):
                    self.command_line_history_idx = len(self.command_line_history) - 1
            elif event.key() == Qt.Key_Down:
                self.command_line_history_idx -= 1
                if self.command_line_history_idx < -1:
                    self.command_line_history_idx = -1
            # If both are then no history
            else:
                return super().eventFilter(source, event)

            # This is reaching end of history (going downwards)
            if self.command_line_history_idx == -1:
                self.commandline_line_edit.setText("")
            else:
                self.commandline_line_edit.setText(self.command_line_history[self.command_line_history_idx])
            return True

        return super().eventFilter(source, event)


class Server(QThread):  # See below

    # TODO: look at server solution that does not depend on Pyqt? Hard to get around singals and QThread nice
    statusBarMessageSignal = pyqtSignal(str, bool)
    logSignal = pyqtSignal(str, str)
    commanderLabelSignal = pyqtSignal(str)
    packetSizeLabelSignal = pyqtSignal(str)
    partyParrotStepSignal = pyqtSignal()
    dataPacketSignal = pyqtSignal(dict)
    # Doing this because we may want to run this server when no
    # graphics are present. Don't want to pass in window that may not exist

    def __init__(self):
        super().__init__()

        self.interface = S2_Interface()
        self.is_active = False

        self.commander: str = None
        # Tracks how many packets have been sent. Do NOT use for any type of guarantees
        self.packet_num = 0
        # Tracks that even if the serial is open, good data may not be coming through
        self.is_actively_receiving_data = False
        # Current server error message
        self.current_error_message = "No Board Connection Attempted"

        # Hold what clients server is connected to
        self.open_client_connections = []

        # Hold commands that will go to the board
        self.command_queue = queue.Queue()

        # Flag and holder for flash dump
        self.do_flash_dump = False
        self.flash_dump_addr: str = None
        self.flash_dump_loc: str = None

        # Holds all the data sent from the boards as a dict. Also contains header that has server connection info
        # For example can call self.data_dict["ec.pressure[0]"] to get the pressure of channel 0 on ec
        self.data_dict = dict()
        self.data_dict["time"] = datetime.now().timestamp()
        self.data_dict["commander"] = self.commander
        self.data_dict["packet_num"] = self.packet_num
        self.data_dict["ser_open"] = self.interface.ser.is_open
        self.data_dict["actively_rx"] = self.is_actively_receiving_data
        self.data_dict["error_msg"] = self.current_error_message

        # Add  all possible channels to the data dict. Best to do it this way because we know everything is there
        # and don't know what we will get in the future
        for channel in self.interface.channels:
            self.data_dict[channel] = 0  # Init all to 0

        self.server_connection_handler = ServerConnectionHandler(self)
        self.server_connection_handler.start()

        # Directory where files are saved
        self.working_directory = "data/"

        # Initialize logs (will be files later in open_base_logs())
        self.server_log: TextIO = None
        self.serial_log: TextIO = None
        self.data_log: TextIO = None
        self.test_data_log: TextIO = None
        self.command_log: TextIO = None
        self.campaign_log: TextIO = None
        self.campaign_location: str = None

        self._averaged_update_freq = -1
        self._num_update_steps = 0
        self._last_update_time = time.time()

        # Start main server thread
        self.start()

    def delayed_init(self):
        """
        This function is called after the ServerGraphics window is done loading because some things need to wait for
        other processes to finish
        :return: None
        """

        # Start logging
        self.update_campaign_logging(None)
        # Have to do this after we start logging obv
        self.logSignal.connect(self.write_to_log)

    def scan(self):
        """
        Scans for comm ports and returns them
        :return: comm ports found
        """
        ports = self.interface.scan()
        self.statusBarMessageSignal.emit("Ports scanned: " + str(ports), False)

        return ports

    def override_commander(self):
        """
        Override the active client commander, set to none
        :return: None
        """

        self.logSignal.emit("Server", "Commander '%s' cleared" % self.commander)
        self.statusBarMessageSignal.emit("Commander '%s' cleared" % self.commander, False)

        self.commander = None

    @property
    def commander(self):
        """
        Gets commander from server
        :return: commander uuid
        """
        return self._commander

    @commander.setter
    def commander(self, value):
        """
        Set commander value. Allows us to always make sure server label is up to date
        :param value: value for commander
        :return: None
        """
        self._commander = value
        self.commanderLabelSignal.emit("Commander UUID: " + str(self._commander))

    def check_commander(self, client_uuid):
        """
        Checks if the uuid passes is the current commander
        :param client_uuid: passed client uuid
        :return: True if uuid is the commander
        """
        if self.commander is None:
            return False

        return client_uuid == self.commander

    def update_packet_header(self):
        """
        Update the data_dict packet header with the current server info
        :return: None
        """
        if self.commander:
            # We are using hash to send out commander so someone else can't spoof it. For example two clients are
            # connected, one is commander. Sending that client UUID to the second client means it could inject that into
            # its packet and then pretend it is commander. Overkill? likely
            self.data_dict["commander"] = hashlib.sha256(self.commander.encode('utf-8')).hexdigest()
        else:
            self.data_dict["commander"] = None
        self.data_dict["packet_num"] = self.packet_num
        # Check if the serial to the board is even open
        self.data_dict["ser_open"] = self.interface.ser.is_open
        self.data_dict["actively_rx"] = self.is_actively_receiving_data
        self.data_dict["error_msg"] = self.current_error_message
        self.data_dict["time"] = datetime.now().timestamp()

    @pyqtSlot(object)
    def client_connection_closed(self, client_handler_thread: ClientConnectionHandler):
        """
        Called from a signal from client handler when connection is closed. Update the commander and remove client
        from open connections
        :param client_handler_thread: client handler thread that needs to be closed
        :return: None
        """
        self.update_commander_from_lost_connection(client_handler_thread.last_uuid)

        # Stop campaign logging if active
        if self.campaign_location is not None:
            self.update_campaign_logging(None)

        if client_handler_thread in self.open_client_connections:
            self.open_client_connections.remove(client_handler_thread)

    def update_commander_from_lost_connection(self, uuid: str):
        """
        Closes the connection with a client.
        :param uuid: last uuid from client closing connection
        :return: None
        """

        if self.commander == uuid:
            self.logSignal.emit("Server", "Lost/ closed commander connection with id (UUID) '%s'" % self.commander)
            self.statusBarMessageSignal.emit("Lost/ closed commander connection with id (UUID) '%s'" % self.commander, False)
            self.commander = None
        else:
            self.logSignal.emit("Server", "Lost/ closed connection to client with id (UUID): %s" % uuid)
            self.statusBarMessageSignal.emit("Lost/ closed connection to client with id (UUID): %s" % uuid, False)

    def connect_to_board(self, port: str, baud: int):
        """
        Attempts a connection to the board through serial COM
        :param port: selected port
        :param baud: selected baud rate
        :return: None
        """

        # Check to make sure port is not none
        if port:
            # This is purposely not in the running section of the thread. If this hangs, indicates a problem so good to
            # show that to the user
            self.interface.connect(port, baud, timeout=0.5)

        if self.interface.ser.isOpen():
            self.logSignal.emit("Server", "Connection established on %s" % port)

        else:
            self.logSignal.emit("Server", "Unable to connect to selected port or no ports available")

    def get_command_list(self):
        """
        Returns a list of all possible commands (commands on board)
        :return: list
        """
        return list(self.interface.get_cmd_names_dict().keys())  # Get all commands to reference

    def get_board_address(self, boardName: str):
        """
        Gets board address from name of the board
        :param boardName: Name of board (as defined in S2 interface)
        :return: board address
        """

        return self.interface.getBoardAddr(boardName)

    def get_command_args(self, command: str):
        """
        Gets a command's args as a list
        :param command: command as string
        :return: list of args
        """

        cmd_id = self.interface.get_cmd_names_dict()[command]
        cmd_args = self.interface.get_cmd_args_dict()[cmd_id]

        return cmd_args

    @pyqtSlot(socket.socket, tuple)
    def create_new_client_connection(self, client_socket: socket.socket, addr: tuple):
        """
        Called from a signal from server connection handler. Creates a new client thread, starts it, connects it,
        and tracks it
        :param client_socket: client socket received from the server connection handler
        :param addr: address of the client (ip)
        :return:
        """

        client = ClientConnectionHandler(client_socket, addr, self)
        self.dataPacketSignal.connect(client.get_new_data_for_client)

        self.open_client_connections.append(client)
        client.start()

    def process_command_line(self, cmd: str, args: list, board_addr: int):
        """
        Processes commands entered through the command line
        :param cmd: command to process
        :param args: command arguments
        :param board_addr: address of board to send to
        :return: Text to be displayed in textbox, if needed
        """

        possible_commands = self.get_command_list()

        # Validate command
        if cmd in possible_commands:
            # TODO:
            pass
            # self.parse_command(cmd, args, board_addr)

        # TODO:
        elif cmd == "auto":  # run an auto sequence
            seq = args[0]
            path = "autos/" + str(seq) + ".txt"

            try:
                with open(path) as f:
                    lines = f.read().splitlines()  # read file

                # create thread to handle auto
                # TODO:
                auto_thread = threading.Thread(target=self.run_auto,
                                               args=(lines, board_addr), daemon=True)
                auto_thread.start()
            except:
                pass

        else:
            return "Command not recognized"

    def exit(self):
        super().exit()
        self.close_logs()
        self.server_connection_handler.exit()

    def shutdown(self):
        """
        Shutdown thread
        :return: Nona
        """
        self.is_active = False

    def open_base_logs(self, runname: str, save_location: str, is_recovered: bool):
        """
        Opens all logs (except test log because that isn't created until a test is created). Can re-open logs that were
        previously closed due to gui crashing
        :param runname: name attached to files, is either the campaign or if no campaign the timestamp
        :param save_location: location files are saved in
        :param is_recovered: if the files should be recovered (re-opened)
        :return: None
        """

        # make data folder if it does not exist
        if not os.path.exists(save_location):
            os.makedirs(save_location)

        # Un lock these files
        if is_recovered:
            os.chmod(save_location + runname + "_server_log.txt", S_IWUSR | S_IREAD)
            os.chmod(save_location + runname + "_serial_log.csv", S_IWUSR | S_IREAD)
            os.chmod(save_location + runname + "_data_log.csv", S_IWUSR | S_IREAD)
            os.chmod(save_location + runname + "_command_log.csv", S_IWUSR | S_IREAD)
            # log file init and headers
            self.server_log = open(save_location + runname + "_server_log.txt", "a+")
            self.serial_log = open(save_location + runname + "_serial_log.csv", "a+")
            self.data_log = open(save_location + runname + "_data_log.csv", "a+")
            self.command_log = open(save_location + runname + "_command_log.csv", "a+")
        else:

            # log file init and headers
            self.server_log = open(save_location + runname + "_server_log.txt", "w")
            self.serial_log = open(save_location + runname + "_serial_log.csv", "w")
            self.data_log = open(save_location + runname + "_data_log.csv", "w")
            self.command_log = open(save_location + runname + "_command_log.csv", "w")

            # Write in the first lines
            self.command_log.write("Time, From Client/ To Board/ To Client, Command/info\n")
            self.serial_log.write("Time, Packet\n")
            # Write header
            self.data_log.write("Time," + self.interface.get_header() + "\n")

    def open_test_log(self, campaign_save_name: str, test_name, is_recovered: bool = False):
        """
        Open logs when a new test is started. We cannot do this with the other base logs because we log those when tests
        are not active
        :param campaign_save_name: save name of the campaign
        :param test_name: name of the test
        :param is_recovered: flag if the test was recovered or not
        :return:
        """

        # make data folder if it does not exist
        if not os.path.exists(self.campaign_location + "tests/"):
            os.makedirs(self.campaign_location + "tests/")

        # Unlock these files
        if is_recovered:
            os.chmod(self.campaign_location + "tests/" + campaign_save_name + "__test__" + test_name +
                     "_data_log.csv", S_IWUSR | S_IREAD)

            # log file init and headers
            self.test_data_log = open(self.campaign_location + "tests/" + campaign_save_name +
                                      "__test__" + test_name + "_data_log.csv", "a+")
        else:
            self.test_data_log = open(
                self.campaign_location + "tests/" + campaign_save_name + "__test__" + test_name + "_data_log.csv", "a+")

            # Write header
            self.test_data_log.write("Time," + self.interface.get_header() + "\n")

    def close_logs(self):
        """
        Closes all logs and locks them
        :return:
        """

        # Check if server log is open, if it is others should also be. Too lazy to check all
        if self.server_log is None:
            return  # Nothing should be open, nothing to close

        # Close all the logs, also lock them from being edited
        self.server_log.close()
        os.chmod(self.server_log.name, S_IREAD | S_IRGRP | S_IROTH)
        self.serial_log.close()
        os.chmod(self.serial_log.name, S_IREAD | S_IRGRP | S_IROTH)
        self.command_log.close()
        os.chmod(self.command_log.name, S_IREAD | S_IRGRP | S_IROTH)
        self.data_log.close()
        os.chmod(self.data_log.name, S_IREAD | S_IRGRP | S_IROTH)

        # Close test logs
        self.close_test_log()

        # Close campaign logs
        if self.campaign_log is not None and not self.campaign_log.closed:
            self.campaign_log.close()
            self.campaign_location = None
            os.chmod(self.campaign_log.name, S_IREAD|S_IRGRP|S_IROTH)

    def close_test_log(self):
        """
        Closes test log. Can't have this as a part of the above close_logs function because it sometimes needs to
        be called independently. For example when a campaign ends, we are going to restart all logging. But when a test
        ends we are going to keep everything else running
        :return:
        """
        if self.test_data_log is not None and not self.test_data_log.closed:
            self.test_data_log.close()
            os.chmod(self.test_data_log.name, S_IREAD | S_IRGRP | S_IROTH)
            self.test_data_log = None

    @pyqtSlot(str, str)
    def write_to_log(self, location: str, msg: str):
        """
        This actually also leverages the logSignal that gets emitted to update the server graphics. That way one only
        one call needs to be made. However is also  directly called
        :param location: String that is either "Server" or "Command" for server and command log respectively
        :param msg: message to log
        :return: None
        """

        if location == "Server":
            self.server_log.write(Constants.getCurrentTimestamp() + msg + "\n")
        elif location == "Command":
            self.command_log.write(Constants.getCurrentTimestamp()+"," + msg + "\n")
        elif location == "Serial":
            self.serial_log.write(Constants.getCurrentTimestamp()+"," + msg + "\n")
        elif location == "Data":
            self.data_log.write(msg + "\n")  # Timestamp already included in data

            # Check if the test log is open (test is running)
            if self.test_data_log is not None:
                self.test_data_log.write(msg + "\n")

    def get_data_dict_as_csv_string(self):
        """
        Returns a string that contains data for all data dict channels
        :return: string of data
        """

        # Get time to start
        data_dict_string = str(self.data_dict["time"]) + ","

        # For all channels (even if not connected), get the data and put it in the string
        for channel in self.interface.channels:
            data_dict_string += "%s," % (self.data_dict[channel])

        return data_dict_string

    def update_campaign_logging(self, campaign_save_name: str, configuration_data: dict = None, avionics_mappings: dict = None):
        """
        Functions updates (starts/ stops) campaign logging. On start config data and avionics mappings are also sent. If
        filename is passed as None then it stops the campaign and starts general logging. If the filename is not none,
        but the configuration data and avionics mappings are, that means the server should recover the campaign
        :param campaign_save_name: save name of campaign
        :param configuration_data: dict of configuration data
        :param avionics_mappings: dict of avionics mappings
        :return: None
        """

        self.close_logs()

        # No campaign, revert to general logging
        if campaign_save_name is None:
            file_timestamp = self.get_file_timestamp_string()
            self.open_base_logs(file_timestamp, self.working_directory + file_timestamp + "/", False)
            self.logSignal.emit("Server", "Raw server logging started under '%s'" % file_timestamp)

        elif configuration_data is None and avionics_mappings is None:  # Check if function call matches recovered state

            self.campaign_location = Constants.campaign_data_dir + campaign_save_name + "/"

            # If this exists then we know we are properly recoverable, otherwise something bad happened
            campaign_dir_exists = os.path.isdir(self.campaign_location)

            if not campaign_dir_exists:
                print(colored("WARNING: Recovered state requested, directory not found"), 'red')
                self.statusBarMessageSignal.emit("Campaign recovery failed. See terminal", True)
                # Restart logging before exiting
                self.update_campaign_logging(None)
                return

            # Re-open base logs with recovered flag
            self.open_base_logs(campaign_save_name, self.campaign_location, is_recovered=True)

            # Re-open campaign log
            os.chmod(self.campaign_location + "campaign_log.txt", S_IWUSR | S_IREAD)
            self.campaign_log = open(self.campaign_location + "campaign_log.txt", "a+")
            self.logSignal.emit("Server", "Campaign '%s' recovered" % campaign_save_name)
            self.campaign_log.write("Campaign %s recovered during new server connection\n" % campaign_save_name)

        elif campaign_save_name is not None and configuration_data is not None and avionics_mappings is not None:
            # Create new campaign logging stuff
            self.campaign_location = Constants.campaign_data_dir + campaign_save_name + "/"

            # Create test folder
            if not os.path.isdir(self.campaign_location + "tests/"):
                os.makedirs(self.campaign_location + "tests/")

            # Open base logs
            self.open_base_logs(campaign_save_name, self.campaign_location, is_recovered=False)

            # Open log and write a few things
            self.campaign_log = open(self.campaign_location + "campaign_log.txt", "w")
            self.campaign_log.write("Campaign started with save name: " + campaign_save_name + "\n")
            self.logSignal.emit("Server", "Campaign '%s' started" % campaign_save_name)

            # Write configuration to file
            with open(self.campaign_location + "configuration.json", "w") as write_file:
                json.dump(configuration_data, write_file, indent="\t")
                os.chmod(write_file.name, S_IREAD | S_IRGRP | S_IROTH)

            # Write avionics mappings to file
            with open(self.campaign_location + "avionicsMappings.csv", "w") as write_file:
                write_file.write("Channel,Name\n")
                for key in avionics_mappings:
                    if key != "Boards":  # currently don't list the boards the user has added
                        write_file.write(avionics_mappings[key][1] + "," + avionics_mappings[key][
                            0] + "\n")  # key is not useful, first index is name, second is channel
                os.chmod(write_file.name, S_IREAD | S_IRGRP | S_IROTH)

        else:
            print(colored("WARNING: Got a call to update_campaign_logging() that should not occur"), 'red')
            self.statusBarMessageSignal.emit("Logging command failed. See terminal", True)
            # Restart logging
            self.update_campaign_logging(None)

    def _calc_server_thread_update_freq(self):
        """
        Function that calculates the update frequency of the run method in the thread. Can let us know if we have too
        much slow code bogging down the server
        :return: None
        """

        self._num_update_steps += 1
        if self._num_update_steps == Constants.SERVER_BOARD_DATA_UPDATE_FREQUENCY:
            self._averaged_update_freq = self._num_update_steps / (time.time() - self._last_update_time)
            #print("Server Run Freq: " + str(self._averaged_update_freq))
            self._num_update_steps = 0
            self._last_update_time = time.time()

    @pyqtSlot(object, dict)
    def process_client_command(self, client_thread: ClientConnectionHandler, command_dict: dict):
        """
        Function for processing any commands from the client. Does not need to be in thread because nothing here should
        be blocking
        :param client_thread: client thread instance in case it needs to be shutdown or something else
        :param command_dict: command dict to pull command and args from
        :return: None
        """

        command = command_dict["command"]
        clientid = command_dict["clientid"]
        args = command_dict["args"]

        if command == Constants.cli_to_ser_cmd_ref["Heartbeat"]:  # Heartbeat, do nothing
            pass

        elif command == Constants.cli_to_ser_cmd_ref["Request Commander"] and self.commander is None:
            self.commander = clientid
            self.logSignal.emit("Server","New commander with UUID: %s" % self.commander)
            self.statusBarMessageSignal.emit("New commander with UUID: %s" % self.commander, False)

        elif command == Constants.cli_to_ser_cmd_ref["Give Commander"] and self.check_commander(clientid):
            self.override_commander()

        elif command == Constants.cli_to_ser_cmd_ref["Board Command"] and self.check_commander(clientid):
            self.command_queue.put(args)

        elif command == Constants.cli_to_ser_cmd_ref["Dump Flash"] and self.check_commander(clientid):
            self.do_flash_dump = True
            self.flash_dump_addr = args

            if self.campaign_log is not None and not self.campaign_log.closed:
                self.flash_dump_loc = self.campaign_location
            else:
                self.flash_dump_loc = None

        elif command == Constants.cli_to_ser_cmd_ref["Campaign Logging"]:
            # If you are like me, I had no idea this * was a thing. Inside a function call that takes a list and
            # expands it as an iterable so you can use a list to call a function. Pretty cool, from here:
            # https://stackoverflow.com/questions/3941517/converting-list-to-args-when-calling-function
            if args is None:
                self.logSignal.emit("Server", ("Campaign '%s' ended" % self.campaign_location).replace(
                    Constants.campaign_data_dir, '').replace("/", ''))
                self.update_campaign_logging(None)
            else:
                self.update_campaign_logging(*args)

        elif command == Constants.cli_to_ser_cmd_ref["Run Autosequence"]:
            # TODO:
            pass
        elif command == Constants.cli_to_ser_cmd_ref["Abort Autosequence"]:
            # TODO:
            pass
        elif command == Constants.cli_to_ser_cmd_ref["Write to Campaign Log"]:
            CET = args[0]
            type_ = args[1]
            text = args[2]

            self.campaign_log.write(CET + " | " + type_ + " | " + text + "\n")

        elif command == Constants.cli_to_ser_cmd_ref["New Test"]:
            campaign_name = args[0]
            test_name = args[1]

            if test_name is not None:
                isRecovered = args[2]
                self.open_test_log(campaign_name, test_name, isRecovered)
            else:
                self.close_test_log()

        elif command == 11:
            self.logSignal.emit("Server", "Connection established with client id (UUID): %s" % clientid)

        elif command not in Constants.cli_to_ser_cmd_ref.values():
            self.statusBarMessageSignal.emit("Warning, Unhandled command from client", True)
            print(colored("WARNING: Recieved command %s from the client which current has no mapping" % str(command),'red'))

        if command !=Constants.cli_to_ser_cmd_ref["Heartbeat"]:
            print(command_dict)
            self.logSignal.emit("Command", "From Client, " + str(command_dict))

    def get_flash_download_progress(self, progress: float):
        """
        This is a callback function from the s2 interface download. Gets the progress and emits a signal to the
        graphics to update
        :param progress: % completed
        :return: None
        """

        self.logSignal.emit("Server", "Flash download progress: %s" % str(progress))

    def run(self):

        # When server is open, should always be attempting this
        while True:
            # Check to see we have good board serial data before sending

            try:
                if self.interface.ser.is_open:

                    # Most important thing lol
                    self.partyParrotStepSignal.emit()

                    # Send commands
                    if not self.command_queue.empty():
                        command_to_send = self.command_queue.get()
                        self.logSignal.emit("Command", "To Board, " + str(command_to_send))
                        self.interface.s2_command(command_to_send)

                    if self.do_flash_dump:
                        # TODO: Is there any reason this can't be in process_commands, I thinknot but then this thread
                        #  would continue and be bad
                        self.logSignal.emit("Server", "Taking a dump. Be out in just a sec")
                        self.interface.download_flash(self.flash_dump_addr, int(
                            datetime.now().timestamp()), self.command_log, self.flash_dump_loc, self.get_flash_download_progress)
                        self.do_flash_dump = False
                        self.flash_dump_loc = None
                        self.flash_dump_addr = None
                        self.logSignal.emit("Server", "Dump Complete. See terminal for more info")
                        self.statusBarMessageSignal.emit("Flash download completed", False)

                    else:
                        # Parse serial, return the board addr the packet originated from & type of packet (data vs cal)
                        board_addr, packet_type = self.interface.parse_serial()
                        self.packet_num += 1

                        # Do some error checking, if the board addr is negative, indicates an error with parser.
                        # More info farther down
                        if board_addr != -1 and board_addr != -2:

                            self.is_actively_receiving_data = True
                            self.current_error_message = "'Norminal' - Jon Insprucker"

                            # Log and update serial packet length
                            self.write_to_log("Serial", str(self.interface.last_raw_packet))
                            self.packetSizeLabelSignal.emit("Last Packet Size: %s" % len(self.interface.last_raw_packet))

                            # Gets new data from the corresponding parser dict
                            if packet_type == Constants.serial_packet_type_ref["Board Data"]:
                                new_data = self.interface.board_parser[board_addr].dict

                            elif packet_type == Constants.serial_packet_type_ref["Calibration Data"]:
                                new_data = self.interface.calibration_parser[board_addr].dict

                            # Get board prefix (like gse., ec., fc.) from board name
                            board_prefix = self.interface.getPrefix(self.interface.getName(board_addr))

                            # Update data dict. Take the prefix + key to build a string that is key for data
                            for key in new_data.keys():
                                self.data_dict[str(board_prefix + key)] = new_data[key]

                        else:
                            # We are here if the parser failed
                            self.is_actively_receiving_data = False

                            # Check which error
                            if board_addr == -1:
                                self.current_error_message = "Serial Parse Failed"
                            elif board_addr == -2:
                                self.current_error_message = "Packet Parse Failed"

                            self.packetSizeLabelSignal.emit("Last Packet Size: %s" % self.current_error_message)

                else:
                    # Serial is closed
                    self.is_actively_receiving_data = False
                    self.packetSizeLabelSignal.emit("Last Packet Size: %s" % "0")
                    with self.command_queue.mutex:
                        self.command_queue.queue.clear()

            except Exception as e:
                print("Server run loop had an error:  ", e)
                self.is_actively_receiving_data = False
                self.packetSizeLabelSignal.emit("Last Packet Size: %s" % "0")
                self.statusBarMessageSignal.emit("Warning: Server run loop error, check terminal", True)

            # Make sure data dict headers are updated
            self.update_packet_header()

            # Only write data to log if we are getting serial data
            if self.is_actively_receiving_data:
                # Write to data log
                self.write_to_log("Data", self.get_data_dict_as_csv_string())

            # Send data dict
            self.dataPacketSignal.emit(self.data_dict)

            # Calc running freq and sleep till next cycle
            self._calc_server_thread_update_freq()
            time.sleep(1/Constants.SERVER_BOARD_DATA_UPDATE_FREQUENCY)

    @staticmethod
    def get_file_timestamp_string():
        """
        Simply returns current time formatted for filename string
        :return: filename timestamp string
        """
        return QDateTime.currentDateTime().date().toString("yyyy-MM-dd") + "-T" + QDateTime.currentDateTime().time().toString("hhmmss")


class ClientConnectionHandler(QThread):
    """
    Processes commands and data sent from the client (GUI/ standalone widgets) to the server. Called the client handler
    because it is handling the connection to the client
    """

    sendToLogSignal = pyqtSignal(str, str)
    connectionClosedSignal = pyqtSignal(object)
    sendProcessCommandSignal = pyqtSignal(object, dict)

    def __init__(self, clientsocket: socket.socket, addr: str, server: Server):
        super().__init__()

        self.client_socket = clientsocket
        self.address = addr
        self.server = server

        self.data_to_client = None

        self.sendToLogSignal.connect(self.server.logSignal)
        self.sendProcessCommandSignal.connect(self.server.process_client_command)
        self.connectionClosedSignal.connect(self.server.client_connection_closed)
        #ConnectionClosedSignal connected in serverHandler class

        self.error_counter = 0

        # This is called 'last' but shouldn't actually change. It is updated every cycle when a command is received
        # from the client but since this class only controls one client (multiple clients = multiple instances) then
        # the uuid should never change. However going to leave it as last_uuid to communicate that it is updated
        self.last_uuid = None

        self.is_active = True

    def shutdown(self):
        """
        Shuts down thread
        :return: None
        """
        self.is_active = False

    def close_connection(self):
        """
        Performs task to close to connection to the client. Either because no data received or requested disconnect
        :return: None
        """
        self.connectionClosedSignal.emit(self)
        self.shutdown()

    @pyqtSlot(dict)
    def get_new_data_for_client(self, data_dict: dict):
        """
        Function called from signal from server class with data. Data is not sent to client immediately, it has to
        wait for this thread to be ready to send data
        :param data_dict: dict of data to sent to client. Contains header + data from board
        :return: None
        """
        # TODO: Rate at which data is sent to client, is tied to speed of heartbeat, if heartbeat is too fast then we
        #  are just sending the same data again. Also need to check that the server is actually getting data at a rate
        #  to support the rate. Ideally will have Constants defined, runtime check, and then verify by calculating real
        #  frequencies

        #  TODO: Maybe also add warning for sending same packet twice without getting update between. Just track last
        #   update time

        # TODO: Final note so I don't forget. The serial call used to read serial in s2interface is blocking.
        #  So no matter what the server update freq is, it will wait for that packet. Need to check this tho

        # ^ Last point seems to be the case. We run at freq of data in. At 10hz have to check GSE rate but I think it
        # is that

        self.data_to_client = data_dict

    def exit(self):
        """
        Called when application exits. Only calls for open connections obviously
        :return: None
        """
        super().exit()

        self.shutdown()

        for open_client_thread in self.open_client_connections:
            open_client_thread.exit()

        # From https://stackoverflow.com/questions/54964856/how-to-interrupt-socket-recv-in-python
        self.client_socket.shutdown(socket.SHUT_RDWR)
        # What is happening here is that the above line prevents client_socket.recv from getting any more recv. To
        # terminate it actually sends an empty packet to the recv which we handle by closing the connection.

    def run(self):

        while self.is_active:
            try:
                # Receive in command/ data from client
                msg = self.client_socket.recv(4096 * 8)  # if the data is ever bigger then this so help me
                if msg == b'':
                    # Remote connection closed

                    self.close_connection()
                    break

                command_dict = pickle.loads(msg)
                self.last_uuid = command_dict["clientid"]
                #print(command_dict)

                # Only want to check for disconnect command here, all else goes to server class for processing
                if command_dict["command"] == 4:  # Disconnect command:
                    self.close_connection()
                    break

                self.sendProcessCommandSignal.emit(self, command_dict)

                data = pickle.dumps(self.data_to_client)
                self.client_socket.sendall(data)

            except Exception as e:
                traceback.print_exc()

        self.client_socket.close()


class ServerConnectionHandler(QThread):
    """
    Simply waits for server to receive a new connection request and then creates a new client handler to deal with it.
    Called the server connection handler because it manages the connection requests to the server handler
    """

    sendToLogSignal = pyqtSignal(str, str)
    sendOpenClientConnectionSignal = pyqtSignal(socket.socket, tuple)

    def __init__(self, server: Server):
        super().__init__()

        self.server = server

        # initialize socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 6969
        # The below line may be my favorite line in the whole server. Found from below link, previously restarting
        # the server quickly after closing it would throw a address in use error, now with this line it does not
        # https://stackoverflow.com/questions/6380057/python-binding-socket-address-already-in-use
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

        self.sendToLogSignal.connect(self.server.logSignal)
        self.sendOpenClientConnectionSignal.connect(self.server.create_new_client_connection)

        self.sock.listen(5)  # TODO: What does this do?

        self.is_active = True

    def shutdown(self):
        self.is_active = False

    def exit(self):
        """
        Called when server exits. Also makes sure all the client sockets are properly closed
        :return:
        """
        super().exit()

        self.shutdown()
        self.sock.close()

    def run(self):
        self.sendToLogSignal.emit("Server", "Server initialized. Waiting for clients to connect...")
        self.sendToLogSignal.emit("Command", "Info, Server initialized. Waiting for commands")
        self.sendToLogSignal.emit("Server", "Listening on %s:%s" % (self.host, self.port))

        while self.is_active:

            # establish connection with client
            try:
                cli, addr = self.sock.accept()

            # When we close the socket it throws and exception that the connection was aborted. We catch that and exit
            except ConnectionAbortedError as e:
                # Safe exit out. Need to return to prevent anything else happening below
                return

            #self.sendToLogSignal.emit("Server", "Opening connection from " + addr[0] + " ...")

            # This creates the thread to handle the client. This method differs from the past. We used to have the
            # server handler class (this class) to create the client thread. However we cannot do that any longer if
            # we wish to communicate through signals from the client handler to the server. Since the server,
            # server handler, and client handler are all threads it gets complicated. If the server handler creates the
            # client handler, due to how PyQt5 handles threads, the client handler is made one a different thread
            # process than the server. As a result any signals the client emits is not handled in a place where the
            # server event loop can handle them.
            self.sendOpenClientConnectionSignal.emit(cli, addr)

        self.sock.close()


if __name__ == '__main__':

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setApplicationName("MASA Server")
    app.setApplicationDisplayName("MASA Server")

    server = ServerGraphics()

    server.show()
    server.exit(app.exec())