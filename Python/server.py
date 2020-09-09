import pickle
import socket
import serial
import serial.tools.list_ports
from PyQt5 import QtGui, QtCore, QtWidgets
f
rom PyQt5.QtCore import Qt
import pyqtgraph as pg
import threading
import ctypes
import os
import sys
from datetime import datetime
from hotfire_packet import ECParse

packet_num = 0
commander = None
dataframe = None
starttime = datetime.now().strftime("%Y%m%d%H%M")

if not os.path.exists("data/" + starttime + "/"):
    os.makedirs("data/" + starttime + "/")

server_log = open('data/'+starttime+"/"+starttime+"_server_log.txt", "w+")


# initialize application
app = QtWidgets.QApplication([])
appid = 'MASA.Server' # arbitrary string
if os.name == 'nt': # Bypass command because it is not supported on Linux 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
else:
    pass
app.setWindowIcon(QtGui.QIcon('logo_ed.png'))

# window layout
top = QtWidgets.QMainWindow()
top.setWindowTitle("Server")
w = QtWidgets.QWidget()
top.setCentralWidget(w)
top_layout = QtWidgets.QGridLayout()
w.setLayout(top_layout)
top.setFixedWidth(1200)
top.setFixedHeight(800)

# server log
log_box  = QtGui.QTextEdit()
log_box.setReadOnly(True)
top_layout.addWidget(log_box, 2, 0)

# send message to log (should work from any thread but it throws a warning after the first attempt)
def send_to_log(text):
    time_obj = datetime.now().time()
    time = "<{:02d}:{:02d}:{:02d}> ".format(time_obj.hour, time_obj.minute, time_obj.second)
    log_box.append(time + text)
    server_log.write(time + text + "\n")

# scan com ports
ports = [p.device for p in serial.tools.list_ports.comports()]

# connect to com port
# ser = serial.Serial(port=None, baudrate=int(alias["BAUDRATE"]), timeout=0.2)
ser = serial.Serial(port=None, baudrate=400000, timeout=0.2)
def connect():
    global ser, ports_box
    if ser.isOpen():
        ser.close()
    try:
        ser.port = str(ports_box.currentText())
        ser.open()
        ser.readline()
        send_to_log("Connection established on %s" % str(ports_box.currentText()))
    except:
        send_to_log("Unable to connect to selected port or no ports available")

# scan for com ports
def scan():
    global ports_box, ports
    ports = [p.device for p in serial.tools.list_ports.comports()]
    ports_box.clear()
    ports_box.addItems(ports)

# set client as commander
def set_commander(clientid, ip):
    global commander
    commander = clientid
    send_to_log("New commander: " + str(clientid) + " (" + str(ip) + ")")

# remove current commander
def override_commander():
    global commander
    send_to_log("Clearing commander")
    commander = None

# connection box (add to top_layout)
connection = QtGui.QGroupBox("EC Connection")
top_layout.addWidget(connection, 0, 0)
connection_layout = QtGui.QGridLayout()
connection.setLayout(connection_layout)
ports_box = QtGui.QComboBox()
connection_layout.addWidget(ports_box, 0, 0, 0, 3)
scanButton = QtGui.QPushButton("Scan")
scanButton.clicked.connect(scan)
connection_layout.addWidget(scanButton, 0, 4)
connectButton = QtGui.QPushButton("Connect")
connectButton.clicked.connect(connect)
connection_layout.addWidget(connectButton, 0, 5)

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

threads = []

# client handler
def client_handler(clientsocket, addr):
    global commander
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
                print(command)
                last_uuid = command["clientid"]
                if command["command"] == 0:
                    pass
                elif (command["command"] == 1 and not commander):
                    set_commander(command["clientid"], addr[0])
                elif (command["command"] == 2 and commander == command["clientid"]):
                    override_commander()
                elif (command["command"] == 4):
                    if commander == command["clientid"]:
                        override_commander()
                    break
                else:
                    print("WARNING: Unhandled command")
                
                packet = {
                    "commander" : commander,
                    "packet_num" : packet_num,
                    "dataframe" : dataframe
                }
                data = pickle.dumps(packet)
                clientsocket.send(data)
            counter = 0 
        except:
            if counter > 5:
                break
            print("Failed Packet (consecutive: %s)" % counter)
            counter += 1

    clientsocket.close()
    send_to_log("Closing connection to " + addr[0])

# main server target function
def server_handler():
    # initialize socket
    s = socket.socket() 
    host = socket.gethostbyname(socket.gethostname())
    port = 6969
    s.bind((host, port))

    # wait
    send_to_log('Server initialized. Waiting for clients to connect...')
    s.listen(5)
    
    #create connection
    while True:
        c, addr = s.accept()     # Establish connection with client.
        send_to_log('Got connection from ' + addr[0])
        t = threading.Thread(target=client_handler, args=(c,addr), daemon=True)
        t.start()
    
    # close socket on exit (i don't think this ever actually will run. need to figure this out)
    s.close()

# start server connection thread
# waits for clients and then creates a thread for each connection
t = threading.Thread(target=server_handler, daemon=True)
t.start()

#menu bar
main_menu = top.menuBar()
main_menu.setNativeMenuBar(True)
file_menu = main_menu.addMenu('&File')

#quit application function
def exit():
    ser.close()
    server_log.close()
    app.quit()
    sys.exit()

#quit application menu item
quit = QtGui.QAction("&Quit", file_menu)
quit.setShortcut("Ctrl+Q")
quit.triggered.connect(exit)
file_menu.addAction(quit)

# initialize parser
parser = ECParse()

# main update loop
def update():
    global packet_num, commander_label, dataframe
    
    try:
        if ser.is_open:
            # read in packet from EC
            serial_packet = ser.readline()

            # unstuff the packet
            unstuffed = b''
            index = int(serial_packet[0])
            for n in range(1, len(serial_packet)):
                temp = serial_packet[n:n+1]
                if(n == index):
                    index = int(serial_packet[n])+n
                    temp = b'\n'
                unstuffed = unstuffed + temp
            serial_packet = unstuffed

            # parse packet
            parser.parse_packet(serial_packet)
            dataframe = parser.dict

    except Exception as e:
        print(e)
        pass
    
    # update server state
    packet_num += 1
    commander_label.setText("Commander: " + str(commander))

#timer and tick updates
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(100) # 10hz

# run
top.show()
app.exec()
exit()