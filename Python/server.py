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
from datetime import datetime

# fake data
dummy_packet = {
    'process_id' : 0,
    'process_name' : 'blah',
    'packetnum' : 0,
    'bool_field' : True,
    'pos' : 1,
    'neg' : -1,
    'field' : 0.34235 }

# initialize application
app = QtWidgets.QApplication([])
appid = 'MASA.Server' # arbitrary string
if os.name == 'nt': # Bypass command because it is not supported on Linux 
	ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
else:
	pass
	# NOTE: On Ubuntu 18.04 this does not need to done to display logo in task bar
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
top_layout.addWidget(log_box, 1, 0)

# send message to log (should work from any thread but it throws a warning after the first attempt)
def send_to_log(text):
    time_obj = datetime.now().time()
    time = "<{:02d}:{:02d}:{:02d}> ".format(time_obj.hour, time_obj.minute, time_obj.second)
    log_box.append(time + text)
    # command_log.write(text + "\n")

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

threads = []

# client handler
def client_handler(clientsocket, addr):
    counter = 0
    while True:
        try:
            msg = clientsocket.recv(1024)
            print(addr[0] + ' >> ' + str(msg))
            if msg.decode("utf-8") == "gimme":
                data = pickle.dumps(dummy_packet)
                clientsocket.send(data)
            elif msg == b'':
                # remote connection closed
                break
            else:
                send_to_log(addr[0] + ' >> ' + str(msg)) 
            counter = 0 
        except:
            if counter > 10:
                break
            print("Failed Packet (consecutive: %s)" % counter)
            counter += 1

    clientsocket.close()
    send_to_log("Closing connection " + addr[0])

# main server target function
def server_handler():
    # initialize socket
    s = socket.socket()         
    host = 'localhost'
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
    app.quit()
    sys.exit()

#quit application menu item
quit = QtGui.QAction("&Quit", file_menu)
quit.setShortcut("Ctrl+Q")
quit.triggered.connect(exit)
file_menu.addAction(quit)

# main update loop
def update():
	dummy_packet["packetnum"] += 1

#timer and tick updates
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(100) # 10hz

# run
top.show()
app.exec()
sys.exit()