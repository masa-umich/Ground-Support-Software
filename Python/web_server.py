import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import dash_bootstrap_components as dbc

import pickle
import socket
import pandas as pd

import threading
import os
import sys
from datetime import datetime
import time
import uuid

from s2Interface import S2_Interface

def client_command(clientid, command, args=()):
    command_dict = {
        "clientid" : clientid,
        "command" : command,
        "args" : args
    }

    return command_dict

# init variables
interface = S2_Interface()
dataframe = []
channels = interface.channels
for c in channels:
    row = {}
    row["Channel"] = c
    row["Value"] = 0
    row["Units"] = interface.units[c]
    dataframe.append(row)
#print(dataframe)

host = '35.3.1.58'
me = socket.gethostbyname(socket.gethostname())
port = 6969
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
clientid = uuid.uuid4().hex
count = 0

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', 'style.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app = dash.Dash(__name__)


app.layout = html.Div([html.Div([dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in ["Channel","Value","Units"]],
    data=dataframe,
    # style_table={
    #             'maxWidth': '50ex',
    #             'overflowY': 'scroll',
    #             'width': '50%',
    #             'minWidth': '50%',
    #         },
    style_cell_conditional=[
        {'if': {'column_id': 'Channel'},
         'width': '15vw'},
        {'if': {'column_id': 'Value'},
         'width': '70vw'},
        {'if': {'column_id': 'Units'},
         'width': '15vw'},
    ],
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }
    ],
    style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold'
    }
),
dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )], style={'width': '60vw'})],
style={'display': 'flex', 'justify-content': 'left'})


@app.callback([Output("table", "data")],
    [Input('interval-component', 'n_intervals')])
def redraw_table(n):
    data = dataframe
    return [data]

def update():
    global dataframe
    while True:
        command = client_command(clientid, 0)
        msg = pickle.dumps(command)
        s.sendall(msg)
        data = s.recv(4096*4)
        packet = pickle.loads(data)
        #print(packet)
        try:
            for i in range(len(channels)):
                dataframe[i]["Value"] = packet[channels[i]]
        except:
            pass
        time.sleep(0.5)
        #print(dataframe)


if __name__ == '__main__':
    timerThread = threading.Thread(target=update)
    timerThread.daemon = True
    timerThread.start()
    #app.run_server(debug=True)
    app.run_server(host='0.0.0.0', debug=False, threaded=True)