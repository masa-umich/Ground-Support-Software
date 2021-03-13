import ctypes
import os
import pickle
import queue
import socket
import sys
import threading
from datetime import datetime
import traceback
import time

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from party import PartyParrot
from s2Interface import S2_Interface

threading.stack_size(134217728)


class Server(QtWidgets.QMainWindow):
    """
    MASA Data Aggregation Server
    """

    def __init__(self):
        """Init server window"""
        super().__init__()

        # init variables
        self.packet_num = 0
        self.packet_size = 0
        self.commander = None
        self.dataframe = {}
        self.starttime = datetime.now().strftime("%Y%m%d%H%M%S")
        self.threads = []
        self.command_queue = queue.Queue()
        self.do_flash_dump = False
        self.dump_addr = None
        self.database_lock = threading.Lock()

        # init logs
        self.server_log = None
        self.serial_log = None
        self.data_log = None
        self.command_log = None

        # initialize parser
        self.interface = S2_Interface()
        self.num_items = len(self.interface.channels)

        # init empty dataframe
        self.dataframe["commander"] = None
        self.dataframe["packet_num"] = 0
        self.dataframe["time"] = datetime.now().timestamp()
        for channel in self.interface.channels:  # hardcoded
            self.dataframe[channel] = 0
        self.dataframe["press.vlv3.en"] = 1

        # init csv header
        self.header = "Time," + self.interface.get_header()
        self.open_log(self.starttime)  # start initial run

        # window layout
        self.setWindowTitle("Server")
        w = QtWidgets.QWidget()
        self.setCentralWidget(w)
        top_layout = QtWidgets.QGridLayout()
        w.setLayout(top_layout)
        base_size = 500
        AR = 1.5  # H/W
        self.setFixedWidth(int(AR * base_size))
        self.setFixedHeight(int(base_size))

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
        connection = QGroupBox("EC Connection")
        top_layout.addWidget(connection, 0, 0)
        connection_layout = QGridLayout()
        connection.setLayout(connection_layout)
        self.packet_size_label = QLabel("Last Packet Size: 0")
        connection_layout.addWidget(self.packet_size_label, 0, 5)
        self.ports_box = QComboBox()
        connection_layout.addWidget(self.ports_box, 0, 0, 0, 2)
        scan_button = QPushButton("Scan")
        scan_button.clicked.connect(self.scan)
        connection_layout.addWidget(scan_button, 0, 3)
        connect_button = QPushButton("Connect")
        connect_button.clicked.connect(self.connect)
        connection_layout.addWidget(connect_button, 0, 4)

        # heartbeat indicator
        self.party_parrot = PartyParrot()
        self.party_parrot.setFixedSize(60, 60)
        top_layout.addWidget(self.party_parrot, 0, 1)

        # populate port box
        self.scan()
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

        # menu bar
        main_menu = self.menuBar()
        main_menu.setNativeMenuBar(True)
        file_menu = main_menu.addMenu('&File')

        # quit application menu item
        quit_action = QAction("&Quit", file_menu)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.exit)
        file_menu.addAction(quit_action)

    def send_to_log(self, textedit: QTextEdit, text: str, timestamp: bool = True):
        """Sends a message to a log.
        (should work from any thread but it throws a warning after the first attempt)
        (also it very rarely breaks)

        Args:
            textedit (QTextEdit): Text box to send to
            text (str): Text to write
            timestamp (bool): add timestamp
        """
        # TODO: Sort this out

        time_obj = datetime.now().time()
        time = "<{:02d}:{:02d}:{:02d}> ".format(
            time_obj.hour, time_obj.minute, time_obj.second)
        if timestamp:
            textedit.append(time + text)
        else:
            textedit.append(text)
        if textedit is self.log_box:
            self.server_log.write(time + text + "\n")

    def connect(self):
        """Connects to COM port"""

        try:
            port = str(self.ports_box.currentText())
            if port:
                self.interface.connect(port, 115200, 0.3)
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
                msg = clientsocket.recv(2048)
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
                    # elif (command["command"] == 6 and commander == command["clientid"]): # checkpoint logs for only commander
                    elif command["command"] == 6:  # checkpoint logs
                        print(command)
                        new_runname = command["args"]

                        if new_runname in (None, ()):
                            runname = datetime.now().strftime("%Y%m%d%H%M%S")
                        elif isinstance(new_runname, str):
                            runname = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + new_runname
                        else:
                            print("Error: Unhandled Runname")

                        self.close_log()
                        self.open_log(runname)
                        self.send_to_log(
                            self.log_box, "Checkpoint Created: %s" % runname)
                    # run autosequence
                    elif command["command"] == 7 and self.commander == command["clientid"]:
                        print(command)
                        addr = command["args"][0]
                        lines = command["args"][1]
                        auto_thread = threading.Thread(target=self.run_auto,
                                                       args=(lines, addr), daemon=True)
                        auto_thread.start()

                    else:
                        print("WARNING: Unhandled command")

                    self.database_lock.acquire()
                    try:
                        self.dataframe["commander"] = self.commander
                        self.dataframe["packet_num"] = self.packet_num
                        data = pickle.dumps(self.dataframe)
                    except:
                        data = None
                    finally:
                        self.database_lock.release()

                    clientsocket.sendall(data)
                counter = 0
            except:  # detect dropped connection
                if counter > 3:  # close connection after 3 consecutive failed packets
                    if self.commander == command["clientid"]:
                        self.override_commander()
                    break
                print("Failed Packet from %s (consecutive: %s)" %
                      (addr[0], counter+1))
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
        if sum([a.isnumeric() for a in args]) == len(cmd_args):
            cmd_dict = {
                "function_name": cmd,
                "target_board_addr": addr,
                "timestamp": int(datetime.now().timestamp()),
                "args": [float(a) for a in args if a.isnumeric()]
            }
            print(cmd_dict)
            self.command_queue.put(cmd_dict)  # add command to queue

    def parse_auto(self, command_list: list, i: int = 0):
        """Recursive autosequence parser

        Args:
            command_list (list): List of autosequence commands
            i (int, optional): Index in autosequence. Defaults to 0.

        Returns:
            list: unrolled autosequence or loop
            int: ending index in autosequence or loop
        """

        commands = list(self.interface.get_cmd_names_dict().keys())
        try:
            # unpack loops and compile into single sequence
            constructed = []
            loop = []
            loop_len = 0
            #in_loop = False
            while i < len(command_list):  # loop parsing
                line = command_list[i]
                cmd = line[0]
                args = line[1:]

                if cmd == "loop":  # start loop
                    loop_len = int(args[0])
                    #in_loop = True
                    (loop, i) = self.parse_auto(command_list, i+1)
                    constructed += (loop * loop_len)
                elif cmd in (commands + ["set_addr", "delay"]):  # add commands to loop
                    constructed.append(line)
                elif cmd == "end_loop":  # stop loop and add to sequence
                    return (constructed, i)

                i+=1
            return (constructed, i)
        except:
            traceback.print_exc()

    
    def run_auto(self, lines: list, addr: int):
        """Runs an autosequence

        Args:
            lines (list): list of autosequence lines
            addr (int): starting target address
        """

        commands = list(self.interface.get_cmd_names_dict().keys())
        try:
            command_list = []
            for line in lines:  # loop parsing
                command_list.append(line.lstrip().lower().split(" "))

            (constructed, _) = self.parse_auto(command_list)
            #print(constructed)
            for cmd_str in constructed:  # run auto
                cmd = cmd_str[0]
                args = cmd_str[1:]

                if cmd == "delay":  # delay time in ms
                    print("delay %s ms" % args[0])
                    time.sleep(float(args[0])/1000)
                elif cmd == "set_addr":  # set target addr
                    print("set_addr %s" % args[0])
                    addr = args[0]
                elif cmd in commands:  # handle commands
                    self.parse_command(cmd, args, addr)

        except:
            traceback.print_exc()

    def command_line_send(self):
        """Processes command line interface"""

        commands = list(self.interface.get_cmd_names_dict().keys())

        cmd_str = self.command_line.text().lower().split(" ")
        addr = self.interface.getBoardAddr(self.board_dropdown.currentText())
        cmd = cmd_str[0]
        args = cmd_str[1:]

        if cmd in commands:
            self.parse_command(cmd, args, addr)

        elif cmd == "help":
            if len(args) == 0:
                self.send_to_log(
                    self.command_textedit, "Enter commands as: <COMMAND> <ARG1> <ARG2> ... <ARGN>\n", timestamp=False)
                self.send_to_log(
                    self.command_textedit, "Available commands:\n%s\n" % commands, timestamp=False)
                self.send_to_log(
                    self.command_textedit, "For more information on a command type: help <COMMAND>\n", timestamp=False)
                self.send_to_log(
                    self.command_textedit, "To run an auto-sequence type: auto <NAME>\nPut your autosequence files in Python/autos/\n", timestamp=False)
            elif args[0] in commands:
                selected_cmd = self.interface.get_cmd_names_dict()[args[0]]
                cmd_args = self.interface.get_cmd_args_dict()[selected_cmd]
                self.send_to_log(self.command_textedit, "Help for: %s (%s)" % (
                    args[0], selected_cmd), timestamp=False)
                self.send_to_log(
                    self.command_textedit, "Args: (arg, format, xmitscale (IGNORE THIS))\n%s" % cmd_args, timestamp=False)

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

    def open_log(self, runname: str):
        """Opens a new set of log files.

        Args:
            runname (str): Run-name label
        """

        # make data folder if it does not exist
        if not os.path.exists("data/" + runname + "/"):
            os.makedirs("data/" + runname + "/")

        # log file init and headers
        self.server_log = open('data/' + runname + "/" +
                               runname + "_server_log.txt", "w+")
        self.serial_log = open('data/' + runname + "/" +
                               runname + "_serial_log.csv", "w+")
        self.data_log = open('data/' + runname + "/" +
                             runname + "_data_log.csv", "w+")
        self.command_log = open('data/' + runname + "/" +
                                runname + "_command_log.csv", "w+")
        self.command_log.write("Time, Command/info\n")
        self.serial_log.write("Time, Packet\n")
        self.data_log.write(self.header + "\n")

    def close_log(self):
        """Safely closes all logfiles"""

        self.server_log.close()
        self.serial_log.close()
        self.command_log.close()
        self.data_log.close()

    def update(self):
        """Main server update loop"""

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
                        datetime.now().timestamp()), self.command_log, "")
                    self.do_flash_dump = False
                    self.send_to_log(self.log_box, "Dump Complete.")

                else:
                    # read in packet from system
                    packet_addr = self.interface.parse_serial()  # returns origin address
                    # packet_addr = -1

                    if packet_addr != -1:
                        # print("PARSER WORKED")
                        raw_packet = self.interface.last_raw_packet
                        self.serial_log.write(datetime.now().strftime(
                            "%H:%M:%S,") + str(raw_packet) + '\n')

                        raw_packet_size = len(raw_packet)
                        self.packet_size_label.setText(
                            "Last Packet Size: %s" % raw_packet_size)
                        # send_to_log(data_box, "Received Packet of length: %s" % raw_packet_size)
                        # disabled to stop server logs becoming massive, see just below send_to_log

                        # parse packet and aggregate
                        new_data = self.interface.board_parser[packet_addr].dict
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
                                # print([n, key, dataframe[key]])

                            self.data_log.write(self.get_logstring() + '\n')
                        finally:
                            self.database_lock.release()
                    else:
                        # send_to_log(data_box, "PARSER FAILED OR TIMEDOUT")
                        pass
            self.party_parrot.step()

        except:
            # traceback.print_exc()
            pass

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
    APPID = 'MASA.DataViewer'  # arbitrary string
    if os.name == 'nt':  # Bypass command because it is not supported on Linux
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
    else:
        pass
        # NOTE: On Ubuntu 18.04 this does not need to done to display logo in task bar
    app.setWindowIcon(QtGui.QIcon('Images/logo_server.png'))

    server = Server()

    # timer and tick updates
    timer = QtCore.QTimer()
    timer.timeout.connect(server.update)
    timer.start(20)  # 50hz

    # run
    server.show()
    server.exit(app.exec())
