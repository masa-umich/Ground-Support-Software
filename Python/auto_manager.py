import sys
import os
import ctypes
#import random
#import json
from datetime import datetime
import ntpath

import pyqtgraph as pg
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt

#from s2Interface import S2_Interface
#from LedIndicatorWidget import LedIndicator
from ClientWidget import ClientWidget, ClientDialog
from parse_auto import parse_auto

class LineTextWidget(QtWidgets.QFrame):
    class NumberBar(QtWidgets.QWidget):
        def __init__(self, *args):
            QtWidgets.QWidget.__init__(self, *args)
            self.edit = None
            # This is used to update the width of the control.
            # It is the highest line that is currently visibile.
            self.highest_line = 0

        def setTextEdit(self, edit):
            self.edit = edit

        def update(self, *args):
            '''
            Updates the number bar to display the current set of numbers.
            Also, adjusts the width of the number bar if necessary.
            '''
            # The + 4 is used to compensate for the current line being bold.
            #width = self.fontMetrics().width(str(self.highest_line)) + 4
            width = int((self.fontMetrics().width(str(self.highest_line)) + 4)*1.5)
            if self.width() != width:
                self.setFixedWidth(width)
            QtWidgets.QWidget.update(self, *args)

        def paintEvent(self, event):
            contents_y = self.edit.verticalScrollBar().value()
            page_bottom = contents_y + self.edit.viewport().height()
            font_metrics = self.fontMetrics()
            current_block = self.edit.document().findBlock(self.edit.textCursor().position())

            painter = QtGui.QPainter(self)
            font = painter.font()
            font.setPointSize(12)
            painter.setFont(font)

            line_count = 0
            # Iterate over all text blocks in the document.
            block = self.edit.document().begin()
            while block.isValid():
                line_count += 1

                # The top left position of the block in the document
                position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()

                # Check if the position of the block is out side of the visible
                # area.
                if position.y() > page_bottom:
                    break

                # We want the line number for the selected line to be bold.
                bold = False
                if block == current_block:
                    bold = True
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)

                # Draw the line number right justified at the y position of the
                # line. 3 is a magic padding number. drawText(x, y, text).
                #painter.drawText(self.width() - font_metrics.width(str(line_count)) - 3, round(position.y()) - contents_y + font_metrics.ascent(), str(line_count))
                painter.drawText(int(self.width() - font_metrics.width(str(line_count))*1.5 - 3), int(round(position.y()) - contents_y + font_metrics.ascent()*1.5), str(line_count))


                # Remove the bold style if it was set previously.
                if bold:
                    font = painter.font()
                    font.setBold(False)
                    painter.setFont(font)

                block = block.next()

            self.highest_line = line_count
            painter.end()

            QtWidgets.QWidget.paintEvent(self, event)


    def __init__(self, *args):
        QtWidgets.QFrame.__init__(self, *args)

        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Sunken)

        self.edit = QtWidgets.QTextEdit()
        self.edit.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.edit.setAcceptRichText(False)
        self.highlighter = Highlighter(self.edit.document())
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setFamily("Consolas")
        self.edit.setFont(font)

        self.number_bar = self.NumberBar()
        self.number_bar.setTextEdit(self.edit)

        hbox = QtWidgets.QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        hbox.addWidget(self.number_bar)
        hbox.addWidget(self.edit)

        self.edit.installEventFilter(self)
        self.edit.viewport().installEventFilter(self)

    def eventFilter(self, object, event):
        # Update the line numbers for all events on the text edit and the viewport.
        # This is easier than connecting all necessary singals.
        if object in (self.edit, self.edit.viewport()):
            self.number_bar.update()
            return False
        return QtWidgets.QFrame.eventFilter(object, event)

    def getTextEdit(self):
        return self.edit

    def getText(self):
        return self.edit.toPlainText()

    def setText(self, text: str):
        self.edit.setText(text)


class Highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent):
        super(Highlighter, self).__init__(parent)
        self.commentFormat = QtGui.QTextCharFormat()
        self.commentFormat.setForeground(QtGui.QColor(34, 139, 34))
        self.cmdFormat = QtGui.QTextCharFormat()
        self.cmdFormat.setForeground(QtCore.Qt.blue)

    def highlightBlock(self, text):
        stripped = text.lstrip()
        if stripped.find(' ') != -1:
            padding = len(text) - len(stripped)
            self.setFormat(0, padding + stripped.find(" "), self.cmdFormat)
        else:
            self.setFormat(0, len(text), self.cmdFormat)
        if text.find('#') != -1:
            self.setFormat(text.find("#"), len(text), self.commentFormat)

class AutoManager(QtWidgets.QMainWindow):
    def __init__(self, client=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.filename = 'Untitled'
        self.path = None
        
        self.setWindowTitle("MASA Script Auto Manager")
        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)
        top_layout = QtWidgets.QVBoxLayout()
        widget.setLayout(top_layout)
        base_size = 850
        AR = 0.7  # H/W
        self.setFixedWidth(int(AR * base_size))
        self.setFixedHeight(int(base_size))

        # menu bar
        main_menu = self.menuBar()
        main_menu.setNativeMenuBar(True)
        options_menu = main_menu.addMenu('&Options')

        # connection menu item
        # set up client
        if not client:
            self.client_dialog = ClientDialog(True)
            self.client = self.client_dialog.client
            connect = QtGui.QAction("&Connection", options_menu)
            # self.quit.setShortcut("Ctrl+K")
            connect.triggered.connect(self.client_dialog.show)
            options_menu.addAction(connect)
            # quit application menu item
            quit = QtGui.QAction("&Quit", options_menu)
            quit.setShortcut("Ctrl+Q")
            quit.triggered.connect(self.exit)
            options_menu.addAction(quit)
            self.is_master = True
        else:
            self.client = client
            self.is_master = False

        # save menu item
        save_action = QtGui.QAction("&Save", options_menu)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save)
        options_menu.addAction(save_action)

        # save as menu item
        saveas_action = QtGui.QAction("&Save As", options_menu)
        saveas_action.setShortcut("Ctrl+Shift+S")
        saveas_action.triggered.connect(self.saveas)
        options_menu.addAction(saveas_action)

        # load menu item
        load_action = QtGui.QAction("&Open", options_menu)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load)
        options_menu.addAction(load_action)

        self.code_area = LineTextWidget()
        top_layout.addWidget(self.code_area)

        self.run_button = QtWidgets.QPushButton("Execute")
        self.run_button.clicked.connect(self.run)
        top_layout.addWidget(self.run_button)
    
    def run(self):
        print(10)
        lines = self.code_area.getText().splitlines()
        command_list = []
        for line in lines:  # loop parsing
            command_list.append(line.lstrip().lower().split(" "))

        (constructed, i) = parse_auto(command_list)
        print(constructed, i)
        if i > 0:
            self.client.command(7, (constructed,))
    
    def save(self):
        if self.path:
            with open(self.path, "w") as f:
                f.write(self.code_area.getText())
        else:
            self.saveas()
    
    def saveas(self):
        savename = QtGui.QFileDialog.getSaveFileName(
            self, 'Save Config', 'autos/'+ self.filename + '.txt', "MASAscript (*.txt)")[0]
        with open(savename, "w") as f:
            f.write(self.code_area.getText())

    def load(self):
        loadname = QtGui.QFileDialog.getOpenFileName(
            self, "Load Auto", "autos/", "MASAScript (*.txt)")[0]
        with open(loadname, "r") as f:
            self.code_area.setText(f.read())
            self.filename = ntpath.basename(loadname).split(".")[0]
            self.path = loadname
    
    def closeEvent(self, event):
        """Handler for closeEvent at window close"""

        self.exit()

    def exit(self):
        """Exit application"""

        if self.is_master:
            self.client.disconnect()
            app.quit()
            sys.exit()


if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()

    # initialize application
    APPID = 'MASA.AutoManager'  # arbitrary string
    if os.name == 'nt':  # Bypass command because it is not supported on Linux
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
    else:
        pass
        # NOTE: On Ubuntu 18.04 this does not need to done to display logo in task bar
    app.setWindowIcon(QtGui.QIcon('Images/logo_server.png'))

    # init window
    CYCLE_TIME = 250  # in ms
    window = AutoManager()

    # timer and tick updates
    cycle_time = 100  # in ms
    timer = QtCore.QTimer()
    timer.timeout.connect(window.client.cycle)
    timer.start(CYCLE_TIME)

    window.show()
    sys.exit(app.exec())
