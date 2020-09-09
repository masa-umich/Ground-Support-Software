from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import ctypes
import os
import pandas as pd

from data_viewer import DataViewer
from hotfire_packet import ECParse

# initialize application
app = QtWidgets.QApplication([])
appid = 'MASA.DataViewer' # arbitrary string
if os.name == 'nt': # Bypass command because it is not supported on Linux 
	ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
else:
	pass
	# NOTE: On Ubuntu 18.04 this does not need to done to display logo in task bar
app.setWindowIcon(QtGui.QIcon('logo_ed.png'))

# layout
top = QtWidgets.QMainWindow()
top.setWindowTitle("MASA Data Viewer")
w = QtWidgets.QWidget()
top.setCentralWidget(w)
top_layout = QtWidgets.QGridLayout()
w.setLayout(top_layout)

# set up environment and database
parser = ECParse()
channels = [item for item in parser.items if (item is not 'zero' and item is not '')]

cols = ['time'] + channels
database = pd.DataFrame(columns=cols)

rows = 3
cols = 3
viewers = [DataViewer(channels) for i in range(rows*cols)]
for i in range(rows):
	for j in range(cols):
		idx = i*3+j
		top_layout.addWidget(viewers[idx], i, j)

# loop
def update():
	per_viewer_actives = [viewer.getActive() for viewer in viewers]
	active_channels = list(set([channel for viewer in per_viewer_actives for channel in viewer])) # kill me now
	#print(active_channels)
	for viewer in viewers:
		if viewer.isActive():
			viewer.update(database)

#timer and tick updates
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(1000)

# run
top.show()
app.exec()