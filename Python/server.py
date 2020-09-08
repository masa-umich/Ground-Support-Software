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

# initialize application
app = QtWidgets.QApplication([])
appid = 'MASA.Server' # arbitrary string
if os.name == 'nt': # Bypass command because it is not supported on Linux 
	ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
else:
	pass
	# NOTE: On Ubuntu 18.04 this does not need to done to display logo in task bar
app.setWindowIcon(QtGui.QIcon('logo_ed.png'))

# layout
top = QtWidgets.QMainWindow()
top.setWindowTitle("Server")
w = QtWidgets.QWidget()
top.setCentralWidget(w)
top_layout = QtWidgets.QGridLayout()
w.setLayout(top_layout)

log_box  = QtGui.QTextEdit()
log_box.setReadOnly(True)
top_layout.addWidget(log_box, 1, 0)

def send_to_log(text):
    time_obj = datetime.now().time()
    time = "<{:02d}:{:02d}:{:02d}> ".format(time_obj.hour, time_obj.minute, time_obj.second)
    log_box.append(time + text)
    # command_log.write(text + "\n")

#scan com ports
ports = [p.device for p in serial.tools.list_ports.comports()]

#connect to com port
#ser = serial.Serial(port=None, baudrate=int(alias["BAUDRATE"]), timeout=0.2)
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

#scan for com ports
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

def on_new_client(clientsocket, addr):
    while True:
        msg = clientsocket.recv(1024)
        send_to_log(addr[0] + ' >> ' + str(msg))
        #data = pickle.dumps(dataframe)
        #clientsocket.send(msg)
        clientsocket.send(msg)
        if msg == b'':
            #remote connection closed
            break
    clientsocket.close()
    send_to_log("Closing connection " + addr[0])

def server_handler():
    global threads, stop_threads
    s = socket.socket()         # Create a socket object
    host = 'localhost'          # Get local machine name
    port = 6969                 # Reserve a port for your service.

    send_to_log('Server started!')
    send_to_log('Waiting for clients...')

    s.bind((host, port))        # Bind to the port
    s.listen(5)                 # Now wait for client connection.
    
    while True:
        c, addr = s.accept()     # Establish connection with client.
        send_to_log('Got connection from ' + addr[0])
        t = threading.Thread(target=on_new_client, args=(c,addr), daemon=True)
        t.start()
        threads.append(t)
    s.close()

t = threading.Thread(target=server_handler, daemon=True)
t.start()
threads.append(t)

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

# loop
def update():
	return

#timer and tick updates
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(1000)

# run
top.show()
app.exec()
sys.exit()