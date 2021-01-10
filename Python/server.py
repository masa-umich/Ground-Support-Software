import json
import pickle
import socket
import serial
import serial.tools.list_ports
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import threading
import ctypes
import os
import sys
import queue
from datetime import datetime
from telemParse import TelemParse
from s2Interface import S2_Interface

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

threading.stack_size(134217728)

# init variables
packet_num = 0
packet_size = 0
commander = None
dataframe = {}
starttime = datetime.now().strftime("%Y%m%d%H%M")
threads = []
command_queue = queue.Queue()

# initialize parser
interface = S2_Interface()

# init empty dataframe (mainly for debugging)
dataframe["commander"] = None
dataframe["packet_num"] = 0
dataframe["time"] = datetime.now().timestamp()
for i in interface.parser.items:
    dataframe[i] = 0
dataframe["vlv3.en"] = 1

# make data folder
if not os.path.exists("data/" + starttime + "/"):
    os.makedirs("data/" + starttime + "/")

# log file init and headers
server_log = open('data/'+starttime+"/"+starttime+"_server_log.txt", "w+")
serial_log = open('data/'+starttime+"/"+starttime+"_serial_log.csv", "w+")
data_log = open('data/'+starttime+"/"+starttime+"_data_log.csv", "w+")
command_log = open('data/'+starttime+"/"+starttime+"_command_log.csv", "w+")
command_log.write("Time, Command/info\n")
serial_log.write("Time, Packet\n")
data_log.write(interface.parser.csv_header)

# initialize application
QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
app = QtWidgets.QApplication([])
appid = 'MASA.Server' # arbitrary string
if os.name == 'nt': # Bypass command because it is not supported on Linux 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
else:
    pass
app.setWindowIcon(QtGui.QIcon('logo_server.png'))

# window layout
top = QtWidgets.QMainWindow()
top.setWindowTitle("Server")
w = QtWidgets.QWidget()
top.setCentralWidget(w)
top_layout = QtWidgets.QGridLayout()
w.setLayout(top_layout)
base_size = 500
AR = 1.5 #H/W
top.setFixedWidth(int(AR*base_size))
top.setFixedHeight(int(base_size))

# server log
tab = QTabWidget()

log_box = QtGui.QTextEdit()
log_box.setReadOnly(True)

data_box = QtGui.QTextEdit()
data_box.setReadOnly(True)
data_box.setLineWrapMode(QTextEdit.NoWrap)

command_textedit = QtGui.QTextEdit()
command_textedit.setReadOnly(True)

tab.addTab(log_box, "Server Log")
tab.addTab(data_box, "Packet Log")
tab.addTab(command_textedit, "Command Log")
top_layout.addWidget(tab, 2, 0)

# send message to log (should work from any thread but it throws a warning after the first attempt, also it very rarely breaks)
def send_to_log(textedit: QTextEdit, text:str):
    time_obj = datetime.now().time()
    time = "<{:02d}:{:02d}:{:02d}> ".format(time_obj.hour, time_obj.minute, time_obj.second)
    textedit.append(time + text)
    server_log.write(time + text + "\n")

# scan com ports
ports = interface.scan()

# connect to com port
# ser = serial.Serial(port=None, baudrate=int(alias["BAUDRATE"]), timeout=0.2)
# ser = serial.Serial(port=None, baudrate=57600, timeout=0.2)
def connect():
    global ports_box, interface
    try:
        port = str(ports_box.currentText())
        interface.connect(port, 115200, 0.2)
        interface.parse_serial()
    except:
        pass

    if interface.ser.isOpen():
        send_to_log(log_box,"Connection established on %s" % port)
    else:
        send_to_log(log_box,"Unable to connect to selected port or no ports available")

# scan for com ports
def scan():
    global ports_box, ports
    ports = interface.scan()
    ports_box.clear()
    ports_box.addItems(ports)

# set client as commander
def set_commander(clientid, ip):
    global commander
    commander = clientid
    send_to_log(log_box, "New commander: " + str(clientid) + " (" + str(ip) + ")")

# remove current commander
def override_commander():
    global commander
    send_to_log(log_box, "Clearing commander")
    commander = None

# connection box (add to top_layout)
connection = QtGui.QGroupBox("EC Connection")
top_layout.addWidget(connection, 0, 0)
connection_layout = QtGui.QGridLayout()
connection.setLayout(connection_layout)
packet_size_label = QtGui.QLabel("Last Packet Size: 0")
connection_layout.addWidget(packet_size_label, 0, 5)
ports_box = QtGui.QComboBox()
connection_layout.addWidget(ports_box, 0, 0, 0, 2)
scanButton = QtGui.QPushButton("Scan")
scanButton.clicked.connect(scan)
connection_layout.addWidget(scanButton, 0, 3)
connectButton = QtGui.QPushButton("Connect")
connectButton.clicked.connect(connect)
connection_layout.addWidget(connectButton, 0, 4)

# populate port box
scan()

# commander status
command_box = QtGui.QGroupBox("Command Status")
top_layout.addWidget(command_box, 1, 0)
command_layout = QtGui.QGridLayout()
command_box.setLayout(command_layout)
commander_label = QtGui.QLabel("Commander: None")
command_layout.addWidget(commander_label, 0, 0, 0, 4)
override_button = QtGui.QPushButton("Override")
override_button.clicked.connect(override_commander)
command_layout.addWidget(override_button, 0, 4)

# client handler
def client_handler(clientsocket, addr):
    global commander, dataframe
    counter = 0
    last_uuid = None
    while True:
        try:
            msg = clientsocket.recv(2048)
            if msg == b'':
                # remote connection closed
                if commander == last_uuid:
                    commander = None
                break
            else:
                command = pickle.loads(msg)
                last_uuid = command["clientid"]
                if command["command"] == 0: # do nothing
                    pass
                elif (command["command"] == 1 and not commander): # take command
                    print(command)
                    set_commander(command["clientid"], addr[0])
                elif (command["command"] == 2 and commander == command["clientid"]): # give up command
                    print(command)
                    override_commander()
                elif (command["command"] == 3 and commander == command["clientid"]): # send command
                    print(command)
                    command_queue.put(command["args"])
                elif (command["command"] == 4): # close connection
                    print(command)
                    if commander == command["clientid"]:
                        override_commander()
                    break
                else:
                    print("WARNING: Unhandled command")
                
                dataframe["commander"] = commander 
                dataframe["packet_num"] = packet_num
                data = pickle.dumps(dataframe)
                clientsocket.sendall(data)
            counter = 0 
        except: # detect dropped connection
            if counter > 3: # close connection after 3 consecutive failed packets
                break
            print("Failed Packet from %s (consecutive: %s)" % (addr[0], counter))
            counter += 1
    clientsocket.close()
    send_to_log(log_box, "Closing connection to " + addr[0])
    t.join()

# main server target function
def server_handler():
    # initialize socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    host = socket.gethostbyname(socket.gethostname())
    port = 6969
    #s.bind(("masadataserver.local", port))
    s.bind((host, port))

    # wait
    send_to_log(log_box,'Server initialized. Waiting for clients to connect...')
    send_to_log(log_box,"Listening on %s:%s" % (host, port))
    s.listen(5)
    
    # create connection
    while True:
        # establish connection with client
        c, addr = s.accept() 
        send_to_log(log_box,'Got connection from ' + addr[0])
        # create thread to handle client
        t = threading.Thread(target=client_handler, args=(c,addr), daemon=True)
        t.start()
    
    # close socket on exit (i don't think this ever actually will run. probably should figure this out)
    s.close()

# start server connection thread
# waits for clients and then creates a thread for each connection
t = threading.Thread(target=server_handler, daemon=True)
t.start()

# menu bar
main_menu = top.menuBar()
main_menu.setNativeMenuBar(True)
file_menu = main_menu.addMenu('&File')

# quit application function
def exit():
    interface.ser.close()
    server_log.close()
    serial_log.close()
    command_log.close()
    data_log.close()
    app.quit()
    sys.exit()

# quit application menu item
quit = QtGui.QAction("&Quit", file_menu)
quit.setShortcut("Ctrl+Q")
quit.triggered.connect(exit)
file_menu.addAction(quit)

# main update loop
def update():
    global packet_num, commander_label, dataframe
    
    try:
        if interface.ser.is_open:
            if not command_queue.empty():
                cmd = command_queue.get()
                send_to_log(command_textedit, str(cmd))
                interface.s2_command(cmd)
                command_log.write(datetime.now().strftime("%H:%M:%S,") + str(cmd)+ '\n')

            # read in packet from EC
            could_parse = interface.parse_serial()

            if could_parse:
                #print("PARSER WORKED")
                raw_packet = interface.last_raw_packet
                serial_log.write(datetime.now().strftime("%H:%M:%S,") + str(raw_packet)+ '\n')

                raw_packet_size = len(raw_packet)
                packet_size_label.setText("Last Packet Size: %s" % raw_packet_size)
                send_to_log(data_box, "Received Packet of length: %s" % raw_packet_size)

                # parse packet
                dataframe = interface.parser.dict
                #print(dataframe)
                dataframe["time"] = datetime.now().timestamp()
                data_log.write(interface.parser.log_string+'\n')
            else:
                send_to_log(data_box, "PARSER FAILED")

    except Exception as e:
        print(e)
        pass
    
    # update server state
    packet_num += 1
    commander_label.setText("Commander: " + str(commander))

# timer and tick updates
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50) # 20hz

# run
top.show()
app.exec()
exit()