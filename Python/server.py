import pickle
import socket
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import threading

def on_new_client(clientsocket,addr):
    while True:
        msg = clientsocket.recv(1024)
        # do some checks and if msg == someWeirdSignal: break:
        print(addr, ' >> ', msg)
        # code here
        clientsocket.send(msg)
        if msg == b'':
            #remote connection closed
            break
    clientsocket.close()
    print("Closing connection", addr)

s = socket.socket()         # Create a socket object
host = 'localhost'          # Get local machine name
port = 6969                 # Reserve a port for your service.

print('Server started!')
print('Waiting for clients...')

s.bind((host, port))        # Bind to the port
s.listen(5)                 # Now wait for client connection.

threads = []
while True:
   c, addr = s.accept()     # Establish connection with client.
   print('Got connection from', addr)
   t = threading.Thread(target=on_new_client, args=(c,addr), daemon=False)
   t.start()
   threads.append(t)
   #Note it's (c,addr) not (addr) because second parameter is a tuple
   #that's how you pass arguments to functions when creating new threads using thread module.
s.close()

#scan com ports
#ports = [p.device for p in serial.tools.list_ports.comports()]

#connect to com port
#ser = serial.Serial(port=None, baudrate=int(alias["BAUDRATE"]), timeout=0.2)
#def connect():
	#global ser, ports_box
	#if ser.isOpen():
		#ser.close()
	#try:
		#ser.port = str(ports_box.currentText())
		#ser.open()
		#ser.readline()
		#print("Connection established on %s" % str(ports_box.currentText()))
	#except:
		#print("Unable to connect to selected port or no ports available")

#scan for com ports
#def scan():
	#global ports_box, ports
	#ports = [p.device for p in serial.tools.list_ports.comports()]
	#ports_box.clear()
	#ports_box.addItems(ports)

# connection box (add to connection_layout)
# connection = QtGui.QGroupBox("Connection")
# sidebar_layout.addWidget(connection)
# connection_layout = QtGui.QGridLayout()
# connection.setLayout(connection_layout)
# scanButton = QtGui.QPushButton("Scan")
# scanButton.clicked.connect(scan)
# connection_layout.addWidget(scanButton, 1, 0, 1, 2)
# connectButton = QtGui.QPushButton("Connect")
# connectButton.clicked.connect(connect)
# connection_layout.addWidget(connectButton, 2, 0, 1, 2)
# ports_box = QtGui.QComboBox()
# connection_layout.addWidget(ports_box, 0, 0)
# heart_beat_indicator = QtGui.QLabel("▖")
# connection_layout.addWidget(heart_beat_indicator, 0, 1)
# connection_layout.setColumnStretch(0, 75)
# connection_layout.setColumnStretch(0, 50)