import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import json
import pickle
import socket
import serial
import serial.tools.list_ports

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
#import pyqtgraph as pg
#import ctypes

import threading
import os
import sys
from datetime import datetime
import time
#from hotfire_packet import ECParse
import queue

# init variables
packet_num = 0
packet_size = 0
commander = None
dataframe = {}
starttime = datetime.now().strftime("%Y%m%d%H%M")
threads = []
command_queue = queue.Queue()

# initialize parser
parser = ECParse()

# make data folder
if not os.path.exists("data/" + starttime + "/"):
    os.makedirs("data/" + starttime + "/")

# log file init and headers
# server_log = open('data/'+starttime+"/"+starttime+"_server_log.txt", "w+")
# serial_log = open('data/'+starttime+"/"+starttime+"_serial_log.csv", "w+")
# data_log = open('data/'+starttime+"/"+starttime+"_data_log.csv", "w+")
# command_log = open('data/'+starttime+"/"+starttime+"_command_log.csv", "w+")
# command_log.write("Time, Command/info\n")
# serial_log.write("Time, Packet\n")
# data_log.write(parser.csv_header)

# scan com ports
#ports = [p.device for p in serial.tools.list_ports.comports()]
# connect to com port
#ser = serial.Serial(port='/dev/ttyACM0', baudrate=57600, timeout=0.2)
ser = serial.Serial(port=None, baudrate=57600, timeout=0.2)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([
    html.Div([
        # dcc.Dropdown(
        # options=[
        #     {'label': 'COM1', 'value': 'COM1'},
        #     {'label': 'COM7', 'value': 'COM7'},
        #     {'label': 'COM10', 'value': 'COM10'}
        # ],
        # value='COM1',
        # clearable=False,
        # searchable=False
        # ),
        # html.Button('Scan', id='scan_button'),
        # html.Button('Connect', id='connect_button'),
        html.Div(id='last_packet_size_label',
                children='Last Packet Size:  '),
        html.Div(id='output_last_packet_size',
                children=packet_size)
    ]),
    html.Br(),
    html.Div([
        html.Div(id='commander_label',
                children='Commander: '),
        html.Div(id='output_commander',
                children='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'),
        html.Button('Override', id='override_button'),
    ]),
    dcc.Textarea(
        value='Log',
        style={'width': '100%'},
        contentEditable=False,
        draggable=False,
        readOnly=False,
        disabled=True
    ),
    dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
])

# send message to log (should work from any thread but it throws a warning after the first attempt, also it very rarely breaks)
def send_to_log(text):
    time_obj = datetime.now().time()
    time = "<{:02d}:{:02d}:{:02d}> ".format(time_obj.hour, time_obj.minute, time_obj.second)
    #log_box.append(time + text)
    #server_log.write(time + text + "\n")




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

@app.callback([Output('output_last_packet_size', 'children'),
    Output('output_commander', 'children')],
    [Input('interval-component', 'n_intervals')])
def redraw_layout(n):
    return packet_size, commander

def update():
    global packet_size
    next_call = time.time()
    while True:
        packet_size += 1
        #print(packet_size)
        next_call = next_call+0.2;
        time.sleep(next_call - time.time())


if __name__ == '__main__':
    timerThread = threading.Thread(target=update)
    timerThread.daemon = True
    timerThread.start()
    app.run_server(debug=True)