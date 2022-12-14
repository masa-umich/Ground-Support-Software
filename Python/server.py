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


from overrides import overrides
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QDateTime, QStandardPaths
from PyQt5.QtWidgets import *

from constants import Constants
from party import PartyParrot
from s2Interface import S2_Interface
import parse_auto

threading.stack_size(134217728)


class Server(QtWidgets.QMainWindow):
    """
    MASA Data Aggregation Server
    """

    def __init__(self, qapp, autoconnect=False):
        """Init server window"""
        super().__init__()

        self.LAUNCH_DIRECTORY = QStandardPaths.writableLocation(QStandardPaths.DataLocation) + "/"

        if not os.path.isdir(self.LAUNCH_DIRECTORY):
            os.mkdir(path=self.LAUNCH_DIRECTORY)

        qapp.setWindowIcon(QtGui.QIcon(self.LAUNCH_DIRECTORY+'Images/logo_server.png'))

        # init variables
        self.packet_num = 0
        self.packet_size = 0
        self.commander = None
        self.dataframe = {}
        self.starttime = QDateTime.currentDateTime().date().toString("yyyy-MM-dd") + "-T" + QDateTime.currentDateTime().time().toString("hhmmss")
        self.threads = []
        self.command_queue = queue.Queue()
        self.log_queue = queue.Queue()
        self.do_flash_dump = False
        self.dump_addr = None
        self.dump_loc = None
        self.database_lock = threading.Lock()
        self.abort_auto = False
        self.is_actively_receiving = False
        self.history_idx = -1
        self.history = []

        # init logs
        self.server_log = None
        self.serial_log = None
        self.data_log = None
        self.test_data_log = None
        self.command_log = None
        self.campaign_log = None
        self.campaign_location = None

        # initialize parser
        self.interface = S2_Interface()
        self.num_items = len(self.interface.channels)

        # init empty dataframe
        self.dataframe["commander"] = None
        self.dataframe["packet_num"] = 0
        self.dataframe["ser_open"] = False
        self.dataframe["actively_rx"] = False
        self.dataframe["error_msg"] = "No Board Connection Attempted"
        self.dataframe["time"] = datetime.now().timestamp()
        for channel in self.interface.channels:  # hardcoded
            self.dataframe[channel] = 0
        self.dataframe["press.vlv3.en"] = 1

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        # init csv header
        self.header = "Time," + self.interface.get_header()
        self.open_log(self.starttime, "data/")  # start initial run

        # window layout
        self.setWindowTitle("Server (" + Constants.GUI_VERSION + ")")
        w = QtWidgets.QWidget()
        self.setCentralWidget(w)
        top_layout = QtWidgets.QGridLayout()
        w.setLayout(top_layout)
        base_size = 500
        AR = 1.5  # H/W
        self.setMinimumWidth(int(AR * base_size))
        self.setMinimumHeight(int(base_size))


        # server log
        tab = QTabWidget()

        packet_widget = QWidget()
        packet_layout = QHBoxLayout()
        packet_widget.setLayout(packet_layout)

        self.data_box = QTextEdit()
        self.data_box.setReadOnly(True)
        self.data_box.setLineWrapMode(QTextEdit.NoWrap)

        command_widget = QWidget()
        command_widget_layout = QVBoxLayout()
        command_widget.setLayout(command_widget_layout)

        # command line interface
        command_line_widget = QWidget()
        command_line_layout = QHBoxLayout()
        command_line_widget.setLayout(command_line_layout)
        self.command_line = QLineEdit()
        self.command_line.returnPressed.connect(self.command_line_send)
        self.command_line.setPlaceholderText(
            "Command line interface. Type \"help\" for info.")
        self.command_line.installEventFilter(self)
        self.board_dropdown = QComboBox()
        self.board_dropdown.addItems(["Engine Controller", "Flight Computer",
                                      "Pressurization Controller", "Recovery Controller", "GSE Controller"])
        command_line_layout.addWidget(self.command_line)
        command_line_layout.addWidget(self.board_dropdown)

        self.command_textedit = QTextEdit()
        self.command_textedit.setReadOnly(True)
        command_widget_layout.addWidget(command_line_widget)
        command_widget_layout.addWidget(self.command_textedit)

        # telemetry table
        self.data_table = QTableWidget()
        self.data_table.setRowCount(self.num_items)
        self.data_table.setColumnCount(3)
        header = self.data_table.horizontalHeader()
        # header.setStretchLastSection(True)
        self.data_table.setHorizontalHeaderLabels(["Channel", "Value", "Unit"])
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        for n in range(self.num_items):
            self.data_table.setItem(
                n, 0, QTableWidgetItem(self.interface.channels[n]))
            self.data_table.setItem(n, 2, QTableWidgetItem(
                self.interface.units[self.interface.channels[n]]))

        packet_layout.addWidget(self.data_box)
        packet_layout.addWidget(self.data_table)

        # tabs
        tab.addTab(self.log_box, "Server Log")
        tab.addTab(packet_widget, "Packet Log")
        tab.addTab(command_widget, "Command Line")
        # top_layout.addWidget(tab, 2, 0) # no parrot
        top_layout.addWidget(tab, 2, 0, 1, 2)

        # please ask Alex before reenabling, need to add circular buffer
        self.send_to_log(self.data_box, "Packet log disabled")

        # connection box (add to top_layout)
        connection = QGroupBox("Serial Port")
        top_layout.addWidget(connection, 0, 0)
        connection_layout = QGridLayout()
        connection.setLayout(connection_layout)
        self.packet_size_label = QLabel("Last Packet Size: 0")
        connection_layout.addWidget(self.packet_size_label, 0, 6)
        self.ports_box = QComboBox()
        connection_layout.addWidget(self.ports_box, 0, 0, 0, 2)
        self.baudrate_box = QComboBox()
        connection_layout.addWidget(self.baudrate_box, 0, 3)
        self.baudrate_box.addItems(["3913043", "115200"])
        scan_button = QPushButton("Scan")
        scan_button.clicked.connect(self.scan)
        connection_layout.addWidget(scan_button, 0, 4)
        connect_button = QPushButton("Connect")
        connect_button.clicked.connect(self.connect)
        connection_layout.addWidget(connect_button, 0, 5)

        # heartbeat indicator
        self.party_parrot = PartyParrot()
        self.party_parrot.setFixedSize(60, 60)
        top_layout.addWidget(self.party_parrot, 0, 1)

        # populate port box
        self.scan()
        if autoconnect:
            self.connect()

        # commander status
        command_box = QGroupBox("Command Status")
        # top_layout.addWidget(command_box, 1, 0) #no parrot
        top_layout.addWidget(command_box, 1, 0, 1, 2)
        command_layout = QGridLayout()
        command_box.setLayout(command_layout)
        self.commander_label = QLabel("Commander: None")
        command_layout.addWidget(self.commander_label, 0, 0, 0, 4)
        override_button = QPushButton("Override")
        override_button.clicked.connect(self.override_commander)
        command_layout.addWidget(override_button, 0, 4)

        # start server connection thread
        # waits for clients and then creates a thread for each connection
        self.t = threading.Thread(target=self.server_handler, daemon=True)
        self.t.start()

        self.send_to_log(self.log_box, "Raw server logging started under '%s'" % self.starttime)

        # menu bar
        main_menu = self.menuBar()
        main_menu.setNativeMenuBar(True)
        file_menu = main_menu.addMenu('&File')

        # quit application menu item
        quit_action = QAction("&Quit", file_menu)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.exit)
        file_menu.addAction(quit_action)

        self.party_parrot.step()

    def send_to_log(self, textedit: QTextEdit, text: str, timestamp: bool = True):
        """Sends a message to a log.

        Args:
            textedit (QTextEdit): Text box to send to
            text (str): Text to write
            timestamp (bool): add timestamp
        """
        self.log_queue.put([textedit, text, timestamp])

    def eventFilter(self, source, event):
        # up and down arrows in command line to see previous commands
        if source is self.command_line and event.type() == QtCore.QEvent.KeyPress:
            if event.key() == Qt.Key_Up:
                self.history_idx += 1
                if self.history_idx >= len(self.history):
                    self.history_idx = len(self.history)-1
            elif event.key() == Qt.Key_Down:
                self.history_idx -= 1
                if self.history_idx < -1:
                    self.history_idx = -1
            else:
                return QtWidgets.QMainWindow.eventFilter(self, source, event)
            #print(self.history_idx)
            if self.history_idx == -1:
                self.command_line.setText("")
            else:
                self.command_line.setText(self.history[self.history_idx])
            return True
        
        return QtWidgets.QMainWindow.eventFilter(self, source, event)

    def connect(self):
        """Connects to COM port"""

        try:
            port = str(self.ports_box.currentText())
            baud = int(self.baudrate_box.currentText())
            if port:
                self.interface.connect(port, baud, 0.5) # 3913043 or 115200
                self.interface.parse_serial()
        except:
            # traceback.print_exc()
            pass

        if self.interface.ser.isOpen():
            self.send_to_log(
                self.log_box, "Connection established on %s" % port)
        else:
            self.send_to_log(
                self.log_box, "Unable to connect to selected port or no ports available")

    def scan(self):
        """Scans for COM ports"""

        ports = self.interface.scan()
        self.ports_box.clear()
        self.ports_box.addItems(ports)

    def set_commander(self, clientid: str, ip: str):
        """Sets a client as commander

        Args:
            clientid (str): UUID of client
            ip (str): IP address of client
        """

        self.commander = clientid
        self.send_to_log(self.log_box, "New commander: " +
                         str(clientid) + " (" + str(ip) + ")")

    def override_commander(self):
        """Removes the current commander"""

        self.send_to_log(self.log_box, "Clearing commander")
        self.commander = None

    def client_handler(self, clientsocket: socket.socket, addr: str):
        """Client thread handler function.

        Args:
            clientsocket (socket.socket): Socket object of new connection
            addr (str): IP address of client connection
        """
        # print(type(clientsocket))
        # client handler
        counter = 0
        last_uuid = None
        while True:
            try:
                msg = clientsocket.recv(4096*8)  # if the data is ever bigger then this so help me
                if msg == b'':
                    # remote connection closed
                    if self.commander == last_uuid:
                        self.commander = None
                    break
                else:
                    command = pickle.loads(msg)
                    last_uuid = command["clientid"]
                    if command["command"] == 0:  # do nothing
                        pass
                    elif command["command"] == 1 and not self.commander:  # take command
                        print(command)
                        self.set_commander(command["clientid"], addr[0])
                    # give up command
                    elif command["command"] == 2 and self.commander == command["clientid"]:
                        print(command)
                        self.override_commander()
                    # send command
                    elif command["command"] == 3 and self.commander == command["clientid"]:
                        print(command)
                        self.command_queue.put(command["args"])
                    elif command["command"] == 4:  # close connection
                        print(command)
                        if self.commander == command["clientid"]:
                            self.override_commander()
                        break
                    # flash dump
                    elif command["command"] == 5 and self.commander == command["clientid"]:
                        print(command)
                        self.do_flash_dump = True
                        self.dump_addr = command["args"]
                        if self.campaign_log is not None and not self.campaign_log.closed:
                            self.dump_loc = self.campaign_location
                        else:
                            self.dump_loc = None

                    # elif (command["command"] == 6 and commander == command["clientid"]): # checkpoint logs for only commander
                    elif command["command"] == 6:  # checkpoint logs
                        print(command)
                        new_runname = command["args"]
                        dictData = None
                        mappings = None
                        if command["args"] is not None and len(command["args"]) > 1:
                            new_runname = command["args"][0]
                            dictData = command["args"][1]
                            mappings = command["args"][2]
                        elif new_runname is not None:
                            new_runname = command["args"][0]
                        self.checkpoint_logs(new_runname, dictData, mappings)
                    # run autosequence
                    elif command["command"] == 7 and self.commander == command["clientid"]:
                        print(command)
                        target_addr = self.interface.getBoardAddr(self.board_dropdown.currentText())
                        lines = command["args"][0]
                        auto_thread = threading.Thread(target=self.run_auto,
                                                       args=(lines, target_addr, True), daemon=True)
                        auto_thread.start()
                    elif command["command"] == 8 and self.commander == command["clientid"]:
                        print(command)
                        with self.command_queue.mutex:
                            self.command_queue.queue.clear()
                        self.abort_auto = True
                    elif command["command"] == 9:
                        print(command)
                        CET = command["args"][0]
                        type_ = command["args"][1]
                        text = command["args"][2]

                        self.campaign_log.write(CET + " | " + type_ + " | " + text + "\n")

                    elif command["command"] == 10:
                        print(command)
                        runname = command["args"][0]
                        testName = command["args"][1]

                        if testName is not None:
                            isRecovered = command["args"][2]
                            self.open_test_log(runname, testName, Constants.campaign_data_dir, isRecovered)
                        else:
                            self.close_test_log()

                    else:
                        print("WARNING: Unhandled command: ", command)

                    self.database_lock.acquire()
                    try:
                        if self.commander:
                            self.dataframe["commander"] = hashlib.sha256(self.commander.encode('utf-8')).hexdigest()
                            #self.dataframe["commander"] = self.commander
                        else:
                            self.dataframe["commander"] = None
                        self.dataframe["packet_num"] = self.packet_num
                        # if the serial to the board is even open
                        self.dataframe["ser_open"] = self.interface.ser.is_open
                        # is actively recieving good data
                        self.dataframe["actively_rx"] = self.is_actively_receiving
                        data = pickle.dumps(self.dataframe)
                    except:
                        data = None
                        traceback.print_exc()
                    finally:
                        self.database_lock.release()

                    clientsocket.sendall(data)
                counter = 0
            except Exception as e:  # detect dropped connection
                print(traceback.format_exc())
                if counter > 3:  # close connection after 3 consecutive failed packets
                    if self.commander == command["clientid"]:
                        self.override_commander()
                    break
                #print(addr)
                print("Failed Packet from %s (consecutive: %s)" % (addr[0], counter+1))
                counter += 1
        clientsocket.close()
        self.send_to_log(self.log_box, "Closing connection to " + addr[0])
        self.t.join()

    def server_handler(self):
        """Handler for server thread. Main server target function."""

        # initialize socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostbyname(socket.gethostname())
        port = 6969
        # s.bind(("masadataserver.local", port))
        sock.bind((host, port))

        # wait
        self.send_to_log(
            self.log_box, 'Server initialized. Waiting for clients to connect...')
        self.send_to_log(self.log_box, "Listening on %s:%s" % (host, port))
        sock.listen(5)

        # create connection
        while True:
            # establish connection with client
            cli, addr = sock.accept()
            self.send_to_log(self.log_box, 'Got connection from ' + addr[0])

            # create thread to handle client
            client_thread = threading.Thread(target=self.client_handler,
                                             args=(cli, addr), daemon=True)
            client_thread.start()

        # close socket on exit (i don't think this ever actually will run. probably should figure this out)
        sock.close()

    # quit application function
    def exit(self):
        """Exits application safely"""

        self.interface.ser.close()
        self.close_log()
        sys.exit()

    def closeEvent(self, event):
        """Handler for closeEvent at window close"""

        self.exit()

    def parse_command(self, cmd: str, args: list, addr: int):
        """Parses a command and compiles the command dict.

        Args:
            cmd (str): Command
            args (list): List of command arguments
            addr (int): Target addr
        """

        selected_cmd = self.interface.get_cmd_names_dict()[cmd]
        cmd_args = self.interface.get_cmd_args_dict()[selected_cmd]

        # make sure it has the right number of args
        #if sum([a.isnumeric() for a in args]) == len(cmd_args):
        try:
            if len(args) == len(cmd_args):
                cmd_dict = {
                    "function_name": cmd,
                    "target_board_addr": int(addr),
                    "timestamp": int(datetime.now().timestamp()),
                    #"args": [float(a) for a in args if a.isnumeric()]
                    "args": [float(a) for a in args]
                }
                print(cmd_dict)
                self.command_queue.put(cmd_dict)  # add command to queue
        except Exception as e:
            print("Error: could not send command because of error ", e)

    def run_auto(self, lines: list, addr: int, remote: bool = False):
        """Runs an autosequence

        Args:
            lines (list): list of autosequence lines
            addr (int): starting target address
            remote (bool): is a pre-parsed auto from remote client
        """

        commands = list(self.interface.get_cmd_names_dict().keys())
        if not remote:
            try:
                command_list = []
                for line in lines:  # loop parsing
                    command_list.append(line.lstrip().lower().split(" "))

                (constructed, _) = parse_auto.parse_auto(command_list)
            except:
                traceback.print_exc()
                return
        else:
            constructed = lines
        
        #print(constructed)
        if len(constructed) == 0:
            self.send_to_log(
                self.command_textedit, "Error in autosequence or autosequence not found", timestamp=False)
        for cmd_str in constructed:  # run auto
            if self.abort_auto:
                with self.command_queue.mutex:
                    self.command_queue.queue.clear()
                self.abort_auto = False
                return
            else:
                cmd = cmd_str[0]
                args = cmd_str[1:]

                if cmd == "delay":  # delay time in ms
                    print("delay %s ms" % args[0])
                    time.sleep(float(args[0])/1000)
                elif cmd == "set_addr":  # set target addr
                    print("set_addr %s" % args[0])
                    addr = args[0]
                elif cmd == "new_log":  # creates new log file
                    
                    if len(args) > 0:
                        print("new_log %s" % args[0])
                        self.checkpoint_logs(args[0], None, None)
                    else:
                        print("new_log")
                        self.checkpoint_logs(None, None, None)
                elif cmd in commands:  # handle commands
                    self.parse_command(cmd, args, addr)

    def startCampaignLogging(self, campaign_save_name, dataDict, avionicsMappings):
        self.close_log()

        recovered_state = os.path.isdir(Constants.campaign_data_dir+campaign_save_name+"/")

        if not os.path.isdir(Constants.campaign_data_dir+campaign_save_name+"/tests/"):
            os.makedirs(Constants.campaign_data_dir+campaign_save_name+"/tests/")

        self.open_log(campaign_save_name, Constants.campaign_data_dir, recovered_state)

        if not recovered_state:
            self.campaign_location = Constants.campaign_data_dir + campaign_save_name + "/"
            self.campaign_log = open(Constants.campaign_data_dir + campaign_save_name + "/campaign_log.txt", "w")
            self.campaign_log.write("Campaign started with save name: " + campaign_save_name + "\n")
            self.send_to_log(self.log_box, "Campaign '%s' started" % campaign_save_name)

            with open(Constants.campaign_data_dir + campaign_save_name + "/configuration.json", "w") as write_file:
                json.dump(dataDict, write_file, indent="\t")
                os.chmod(write_file.name, S_IREAD | S_IRGRP | S_IROTH)

            with open(Constants.campaign_data_dir + campaign_save_name + "/avionicsMappings.csv", "w") as write_file:
                write_file.write("Channel,Name\n")
                for key in avionicsMappings:
                    if key != "Boards":  # currently don't list the boards the user has added
                        write_file.write(avionicsMappings[key][1] + "," + avionicsMappings[key][
                            0] + "\n")  # key is not useful, first index is name, second is channel
                os.chmod(write_file.name, S_IREAD | S_IRGRP | S_IROTH)
        else:
            os.chmod(Constants.campaign_data_dir + campaign_save_name + "/campaign_log.txt", S_IWUSR | S_IREAD)
            self.campaign_location = Constants.campaign_data_dir + campaign_save_name + "/"
            self.campaign_log = open(Constants.campaign_data_dir + campaign_save_name + "/campaign_log.txt", "a+")
            self.send_to_log(self.log_box, "Campaign '%s' recovered" % campaign_save_name)
            self.campaign_log.write("Campaign %s recovered during new server connection\n" % campaign_save_name)

    def checkpoint_logs(self, filename, dataDict, avionicsMappings):
        if filename in (None, (), []):
            runname = QDateTime.currentDateTime().date().toString("yyyy-MM-dd") + "-T" + QDateTime.currentDateTime().time().toString("hhmmss")
        elif isinstance(filename, str):
            self.startCampaignLogging(filename, dataDict, avionicsMappings)
            return
        else:
            print("Error: Unhandled Runname")

        self.close_log()
        self.open_log(runname, "data/")
        self.send_to_log(self.log_box, "Raw server logging started under '%s'" % runname)

    def getHelp(self, selected_command):
        commands = list(self.interface.get_cmd_names_dict().keys())
        keywords = ["set_addr", "delay", "auto"] + commands

        tooltips = {}
        for cmd in commands:
            cmd_id = self.interface.get_cmd_names_dict()[cmd]
            cmd_args = self.interface.get_cmd_args_dict()[cmd_id]
            tip = "%s" % cmd  
            for arg in cmd_args:
                name = arg[0]
                arg_type = arg[1]
                tip += " %s(%s)" % (name, arg_type)
            tooltips[cmd] = tip
        tooltips["delay"] = "delay time(int, milliseconds)"
        tooltips["set_addr"] = "set_addr target_addr(int)"
        tooltips["auto"] = "auto auto_name(str)"
        tooltips["new_log"] = "new_log logname(str)"

        return tooltips[selected_command]

    def command_line_send(self):
        """Processes command line interface"""

        commands = list(self.interface.get_cmd_names_dict().keys())

        self.history = [self.command_line.text()] + self.history
        self.history_idx = -1
        #print(self.history)
        cmd_str = self.command_line.text().lower().split(" ")
        addr = self.interface.getBoardAddr(self.board_dropdown.currentText())
        cmd = cmd_str[0]
        args = cmd_str[1:]

        if cmd in commands:
            self.parse_command(cmd, args, addr)

        elif cmd == "help":
            if len(args) == 0:
                self.send_to_log(
                    self.command_textedit, "Enter commands as: <COMMAND> <ARG1> <ARG2> ... <ARGN>\n\nAvailable commands:\n%s\n\nFor more information on a command type: help <COMMAND>\n\nTo run an auto-sequence type: auto <NAME>\nPut your autosequence files in Python/autos/\n" % commands, timestamp=False)
            elif args[0] in (["set_addr", "delay", "auto", "new_log"] + commands):
                selected_cmd = args[0]
                cmd_args = self.getHelp(selected_cmd)
                self.send_to_log(
                    self.command_textedit, "Help for: %s\nArgs: arg(format)\n%s" % (selected_cmd, cmd_args), timestamp=False)

        elif cmd == "auto":  # run an auto sequence
            seq = args[0]
            path = "autos/" + str(seq) + ".txt"

            try:
                with open(path) as f:
                    lines = f.read().splitlines()  # read file

                # create thread to handle auto
                auto_thread = threading.Thread(target=self.run_auto,
                                               args=(lines, addr), daemon=True)
                auto_thread.start()
            except:
                pass
        
        elif cmd == "new_log":
            #print("new_log %s" % args[0])
            if len(args) > 0:
                self.checkpoint_logs(args[0], None, None)
            else:
                self.checkpoint_logs(None, None, None)

        self.command_line.clear()

    # get data formatted for csv
    def get_logstring(self):
        """Constructs a datalog CSV row from current data

        Returns:
            str: Formatted CSV row
        """

        logstring = str(self.dataframe["time"]) + ","
        for channel in self.interface.channels:
            logstring += "%s," % (self.dataframe[channel])
        return logstring

    def open_log(self, runname: str, save_location: str, is_recovered: bool = False):
        """Opens a new set of log files.

        Args:
            runname (str): Run-name label
            save_location (str): location where to save logs, must have ending /
            is_recovered (bool): pass in true if you are opening logs that were previously open. Does not write new
            headers
        """

        # make data folder if it does not exist
        if not os.path.exists(save_location + runname + "/"):
            os.makedirs(save_location + runname + "/")

        # Un lock these files
        if is_recovered:
            os.chmod(save_location + runname + "/" + runname + "_server_log.txt", S_IWUSR | S_IREAD)
            os.chmod(save_location + runname + "/" + runname + "_serial_log.csv", S_IWUSR | S_IREAD)
            os.chmod(save_location + runname + "/" + runname + "_data_log.csv", S_IWUSR | S_IREAD)
            os.chmod(save_location + runname + "/" + runname + "_command_log.csv", S_IWUSR | S_IREAD)
            # log file init and headers
            self.server_log = open(save_location + runname + "/" +
                                   runname + "_server_log.txt", "a+")
            self.serial_log = open(save_location + runname + "/" +
                                   runname + "_serial_log.csv", "a+")
            self.data_log = open(save_location + runname + "/" +
                                 runname + "_data_log.csv", "a+")
            self.command_log = open(save_location + runname + "/" +
                                    runname + "_command_log.csv", "a+")
        else:

            # log file init and headers
            self.server_log = open(save_location + runname + "/" +
                                   runname + "_server_log.txt", "w")
            self.serial_log = open(save_location + runname + "/" +
                                   runname + "_serial_log.csv", "w")
            self.data_log = open(save_location + runname + "/" +
                                 runname + "_data_log.csv", "w")
            self.command_log = open(save_location + runname + "/" +
                                    runname + "_command_log.csv", "w")
            self.command_log.write("Time, Command/info\n")
            self.serial_log.write("Time, Packet\n")
            self.data_log.write(self.header + "\n")

    def open_test_log(self, runname:str, test_name, save_location: str, is_recovered: bool = False):

        # make data folder if it does not exist
        if not os.path.exists(save_location + runname + "/tests/"):
            os.makedirs(save_location + runname + "/tests/")

        # Un lock these files
        if is_recovered:
            os.chmod(save_location + runname + "/tests/" + runname + "__test__" + test_name + "_data_log.csv", S_IWUSR | S_IREAD)
            # log file init and headers
            self.test_data_log = open(save_location + runname + "/tests/" + runname + "__test__" + test_name + "_data_log.csv", "a+")
        else:
            self.test_data_log = open(
                save_location + runname + "/tests/" + runname + "__test__" + test_name + "_data_log.csv", "a+")

            self.test_data_log.write(self.header + "\n")

    def close_test_log(self):
        if self.test_data_log is not None and not self.test_data_log.closed:
            self.test_data_log.close()
            os.chmod(self.test_data_log.name, S_IREAD | S_IRGRP | S_IROTH)
            self.test_data_log = None

    def close_log(self):
        """Safely closes all logfiles"""

        self.server_log.close()
        os.chmod(self.server_log.name, S_IREAD | S_IRGRP | S_IROTH)
        self.serial_log.close()
        os.chmod(self.serial_log.name, S_IREAD | S_IRGRP | S_IROTH)
        self.command_log.close()
        os.chmod(self.command_log.name, S_IREAD | S_IRGRP | S_IROTH)
        self.data_log.close()
        os.chmod(self.data_log.name, S_IREAD | S_IRGRP | S_IROTH)

        self.close_test_log()

        if self.campaign_log is not None and not self.campaign_log.closed:
            self.campaign_log.close()
            self.campaign_location = None
            os.chmod(self.campaign_log.name, S_IREAD|S_IRGRP|S_IROTH)

    @overrides
    def update(self):
        """Main server update loop"""
        super().update()
        
        if not self.log_queue.empty():
            log_args = self.log_queue.get()
            textedit = log_args[0]
            text = log_args[1]
            timestamp = log_args[2]

            time_obj = datetime.now().time()
            time = "<{:02d}:{:02d}:{:02d}> ".format(time_obj.hour, time_obj.minute, time_obj.second)
            if timestamp:
                textedit.append(time + text)
            else:
                textedit.append(text)
            if textedit is self.log_box:
                self.server_log.write(time + text + "\n")

        try:
            if self.interface.ser.is_open:
                if not self.command_queue.empty():
                    cmd = self.command_queue.get()
                    self.send_to_log(self.command_textedit, str(cmd))
                    self.interface.s2_command(cmd)
                    self.command_log.write(datetime.now().strftime(
                        "%H:%M:%S,") + str(cmd) + '\n')

                if self.do_flash_dump:
                    self.send_to_log(
                        self.log_box, "Taking a dump. Be out in just a sec")
                    QApplication.processEvents()
                    self.interface.download_flash(self.dump_addr, int(
                        datetime.now().timestamp()), self.command_log, self.dump_loc)
                    self.do_flash_dump = False
                    self.dump_loc = None
                    self.send_to_log(self.log_box, "Dump Complete.")

                else:
                    # read in packet from system
                    packet_addr, packet_type = self.interface.parse_serial()  # returns origin address
                    # packet_addr = -1
                    if packet_addr != -1 and packet_addr != -2:
                        # print("PARSER WORKED")
                        self.is_actively_receiving = True
                        self.dataframe["error_msg"] = "'Norminal' - Jon Insprucker"

                        raw_packet = self.interface.last_raw_packet
                        self.serial_log.write(datetime.now().strftime(
                            "%H:%M:%S,") + str(raw_packet) + '\n')

                        raw_packet_size = len(raw_packet)
                        self.packet_size_label.setText(
                            "Last Packet Size: %s" % raw_packet_size)
                        # send_to_log(data_box, "Received Packet of length: %s" % raw_packet_size)
                        # disabled to stop server logs becoming massive, see just below send_to_log

                        # parse packet and aggregate

                        # default to board_parser
                        new_data = self.interface.board_parser[packet_addr].dict

                        # Override with correct parser if packet type != 0
                        if (packet_type == 2):
                            new_data = self.interface.calibration_parser[packet_addr].dict
                        # New parsers get called here as they get added

                        prefix = self.interface.getPrefix(
                            self.interface.getName(packet_addr))

                        self.database_lock.acquire()
                        try:
                            for key in new_data.keys():
                                self.dataframe[str(
                                    prefix + key)] = new_data[key]

                            # print(dataframe)
                            self.dataframe["time"] = datetime.now().timestamp()
                            for n in range(self.num_items):
                                key = self.interface.channels[n]
                                self.data_table.setItem(
                                    n, 1, QTableWidgetItem(str(self.dataframe[key])))
                                #print([n, key, dataframe[key]])

                            self.data_log.write(self.get_logstring() + '\n')

                            if self.test_data_log is not None:
                                self.test_data_log.write(self.get_logstring() + '\n')
                        finally:
                            self.database_lock.release()
                    else:

                        # send_to_log(data_box, "PARSER FAILED OR TIMEDOUT")
                        self.is_actively_receiving = False
                        if packet_addr == -1:
                            self.dataframe["error_msg"] = "Serial Parse Failed"
                        elif packet_addr == -2:
                            self.dataframe["error_msg"] = "Packet Parse Failed"

                        self.packet_size_label.setText("Last Packet Size: %s" % self.dataframe["error_msg"])
                        pass
            else:
                self.packet_size_label.setText("Last Packet Size: %s" % "0")
                self.is_actively_receiving = False

            self.party_parrot.step()

        except Exception as e:
            #traceback.print_exc()
            print("Parser failed with error ", e)
            self.is_actively_receiving = False
            self.packet_size_label.setText("Last Packet Size: %s" % "Exception, check terminal")

        # update server state
        self.packet_num += 1
        self.commander_label.setText("Commander: " + str(self.commander))


if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()

    # initialize application
    APPID = 'MASA.Server'  # arbitrary string
    if os.name == 'nt':  # Bypass command because it is not supported on Linux
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
    else:
        pass
        # NOTE: On Ubuntu 18.04 this does not need to done to display logo in task bar
    app.setApplicationName("MASA Server")
    app.setApplicationDisplayName("MASA Server")

    if len(sys.argv) > 1:
        if sys.argv[1] == "--connect":
            server = Server(app, autoconnect=True)
        else:
            server = Server(app, autoconnect=False)
    else:
        server = Server(app, autoconnect=False)

    # timer and tick updates
    timer = QtCore.QTimer()
    timer.timeout.connect(server.update)
    timer.start(20)  # 50hz

    # run
    server.show()
    server.exit(app.exec())
