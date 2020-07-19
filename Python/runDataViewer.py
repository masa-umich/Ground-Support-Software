from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from data_viewer import DataViewer
import ctypes
import os

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
for i in range(3):
    for j in range(3):
        top_layout.addWidget(DataViewer(), i, j)

# run
top.show()
app.exec()