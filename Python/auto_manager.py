import sys
import os
import ctypes
import ntpath

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
from overrides import overrides

from s2Interface import S2_Interface
from ClientWidget import ClientDialog
from parse_auto import parse_auto

INTERFACE = S2_Interface()
COMMANDS = list(INTERFACE.get_cmd_names_dict().keys())
KEYWORDS = ["set_addr", "delay", "loop", "end_loop", "auto", "new_log"] + COMMANDS

TOOLTIPS = {}
for cmd in COMMANDS:
    cmd_id = INTERFACE.get_cmd_names_dict()[cmd]
    cmd_args = INTERFACE.get_cmd_args_dict()[cmd_id]
    tip = "<nobr><b>%s</b>" % cmd  
    for arg in cmd_args:
        name = arg[0]
        arg_type = arg[1]
        tip += " %s<i>(%s)</i>" % (name, arg_type)
    TOOLTIPS[cmd] = tip + "</nobr>"
TOOLTIPS["delay"] = "<nobr><b>delay</b> time<i>(int, milliseconds)</i></nobr>"
TOOLTIPS["set_addr"] = "<nobr><b>set_addr</b> target_addr<i>(int)</i></nobr>"
TOOLTIPS["loop"] = "<nobr><b>loop</b> num_loops<i>(int)</i></nobr>"
TOOLTIPS["end_loop"] = "<nobr><b>end_loop</b></nobr>"
TOOLTIPS["auto"] = "<nobr><b>auto</b> auto_name<i>(str)</i></nobr>"
TOOLTIPS["new_log"] = "<nobr><b>new_log</b> logname<i>(str)</i></nobr>"

class DictionaryCompleter(QtGui.QCompleter):
    insertText = QtCore.pyqtSignal(str)

    def __init__(self, keywords=None, parent=None):
        keywords = KEYWORDS
        QtGui.QCompleter.__init__(self, keywords, parent)
        self.activated.connect(self.changeCompletion)

    def changeCompletion(self, completion):
        if completion.find("(") != -1:
            completion = completion[:completion.find("(")]
        # print(completion)
        self.insertText.emit(completion)


class AutoTextEdit(QtGui.QTextEdit):
    def __init__(self, *args):
        # *args to set parent
        QtGui.QLineEdit.__init__(self, *args)
        self.completer = None

    def setCompleter(self, completer):
        if self.completer:
            self.disconnect(self.completer, 0, self, 0)
        if not completer:
            return

        completer.setWidget(self)
        completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer = completer
        self.completer.insertText.connect(self.insertCompletion)

    def insertCompletion(self, completion):
        tc = self.textCursor()
        extra = (len(completion) -
                 len(self.completer.completionPrefix()))
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        return tc.selectedText()
    
    def textUnderMouse(self):
        oldCur = self.textCursor()
        textCursor = self.cursorForPosition(self.mapFromGlobal(QtGui.QCursor().pos()))
        textCursor.select(QtGui.QTextCursor.WordUnderCursor)
        self.setTextCursor(textCursor)
        word = self.textCursor().selectedText()
        self.setTextCursor(oldCur)
        return word
    
    @overrides
    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self)
        QtGui.QTextEdit.focusInEvent(self, event)

    @overrides
    def keyPressEvent(self, event):
        if self.completer and self.completer.popup() and self.completer.popup().isVisible():
            if event.key() in (
                    QtCore.Qt.Key_Enter,
                    QtCore.Qt.Key_Return,
                    QtCore.Qt.Key_Escape,
                    QtCore.Qt.Key_Tab,
                    QtCore.Qt.Key_Backtab):
                event.ignore()
                return
        # has ctrl-Space been pressed?
        isShortcut = (event.modifiers() == QtCore.Qt.ControlModifier and
                      event.key() == QtCore.Qt.Key_Space)
        # modifier to complete suggestion inline ctrl-e
        inline = (event.modifiers() == QtCore.Qt.ControlModifier and
                  event.key() == QtCore.Qt.Key_E)
        
        help_tip = event.key() == QtCore.Qt.Key_F1
        if help_tip:
            #phrase = self.textUnderMouse().lower() # at mouse pointer
            phrase = self.textUnderCursor().lower() # at text cursor
            if phrase in KEYWORDS:
                QtWidgets.QToolTip.showText(QtGui.QCursor().pos(), TOOLTIPS[phrase], self, QtCore.QRect())
                #print(phrase)
        
        # if inline completion has been chosen
        if inline:
            # set completion mode as inline
            self.completer.setCompletionMode(QtGui.QCompleter.InlineCompletion)
            completionPrefix = self.textUnderCursor()
            if (completionPrefix != self.completer.completionPrefix()):
                self.completer.setCompletionPrefix(completionPrefix)
            self.completer.complete()
            # set the current suggestion in the text box
            self.completer.insertText.emit(self.completer.currentCompletion())
            # reset the completion mode
            self.completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
            return
        if (not self.completer or not isShortcut):
            pass
            QtGui.QTextEdit.keyPressEvent(self, event)
        ctrlOrShift = event.modifiers() in (QtCore.Qt.ControlModifier,
                                            QtCore.Qt.ShiftModifier)
        if ctrlOrShift and event.text() == '':
            return
        eow = "~!@#$%^&*+{}|:\"<>?,./;'[]\\-="  # end of word

        hasModifier = ((event.modifiers() != QtCore.Qt.NoModifier) and
                       not ctrlOrShift)

        completionPrefix = self.textUnderCursor()
        if not isShortcut:
            if self.completer.popup():
                self.completer.popup().hide()
            return

        self.completer.setCompletionPrefix(completionPrefix)
        popup = self.completer.popup()
        popup.setCurrentIndex(
            self.completer.completionModel().index(0, 0))
        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0)
                    + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)  # popup


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
            painter.drawText(int(self.width() - font_metrics.width(str(line_count))*1.5 - 3), int(
                round(position.y()) - contents_y + font_metrics.ascent()*1.5), str(line_count))

            # Remove the bold style if it was set previously.
            if bold:
                font = painter.font()
                font.setBold(False)
                painter.setFont(font)

            block = block.next()

        self.highest_line = line_count
        painter.end()

        QtWidgets.QWidget.paintEvent(self, event)


class LineTextWidget(QtWidgets.QFrame):
    def __init__(self, *args):
        QtWidgets.QFrame.__init__(self, *args)

        self.setFrameStyle(QtWidgets.QFrame.StyledPanel |
                           QtWidgets.QFrame.Sunken)

        self.edit = AutoTextEdit()
        self.edit.setCompleter(DictionaryCompleter())
        self.edit.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.edit.setAcceptRichText(False)
        self.highlighter = Highlighter(self.edit.document())
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setFamily("Consolas")
        self.edit.setFont(font)

        self.number_bar = NumberBar()
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
    def __init__(self, gui = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.filename = 'Untitled'
        self.path = None
        self._gui = gui

        self.setWindowTitle("MASAscript Auto Manager")
        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)
        top_layout = QtWidgets.QVBoxLayout()
        widget.setLayout(top_layout)
        base_size = 850
        AR = 0.7  # H/W
        self.setFixedWidth(int(AR * base_size))
        self.setFixedHeight(int(base_size))
        self.setMouseTracking(True)

        # menu bar
        main_menu = self.menuBar()
        main_menu.setNativeMenuBar(True)
        options_menu = main_menu.addMenu('&Options')

        # connection menu item
        # set up client
        # if not client:
        #     self.client_dialog = ClientDialog(True)
        #     self.client = self.client_dialog.client
        #     connect = QtGui.QAction("&Connection", options_menu)
        #     # self.quit.setShortcut("Ctrl+K")
        #     connect.triggered.connect(self.client_dialog.show)
        #     options_menu.addAction(connect)
        #     # quit application menu item
        #     quit = QtGui.QAction("&Quit", options_menu)
        #     quit.setShortcut("Ctrl+Q")
        #     quit.triggered.connect(self.exit)
        #     options_menu.addAction(quit)
        #     self.is_master = True
        # else:
        #     self.client = client
        #     self.is_master = False
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
        self.code_area.setMouseTracking(True)

        butt_layout = QtWidgets.QHBoxLayout()
        self.run_button = QtWidgets.QPushButton("Execute")
        self.run_button.clicked.connect(self.run)
        self.abort_button = QtWidgets.QPushButton("Abort")
        self.abort_button.clicked.connect(self.abort)
        butt_layout.addWidget(self.run_button)
        butt_layout.addWidget(self.abort_button)
        top_layout.addLayout(butt_layout)

    def run(self):
        code = self.code_area.getText()
        lines = code.splitlines()
        command_list = []
        for line in lines:  # loop parsing
            command_list.append(line.lstrip().lower().split(" "))
        
        # minor code validation
        first_pharses = [c[0] for c in command_list]
        if first_pharses.count("set_addr") < 1:
            self.showDialog("set_addr command missing. Please set the target address.")
        elif first_pharses.count("loop") != first_pharses.count("end_loop"):
            self.showDialog("Mismatched loop and end_loop statements. Number must match.")
        else:
            (constructed, i) = parse_auto(command_list)
            print(constructed, i)
            if i > 0:
                self._gui.liveDataHandler.sendCommand(7, (constructed,))
    
    def showDialog(self, msg):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Critical)
        msgBox.setText(msg)
        msgBox.setWindowTitle("Error")
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        return msgBox.exec()

    def abort(self):
        self._gui.liveDataHandler(8)

    def save(self):
        if self.path:
            with open(self.path, "w") as f:
                f.write(self.code_area.getText())
        else:
            self.saveas()

    def saveas(self):
        savename = QtGui.QFileDialog.getSaveFileName(
            self, 'Save Config', 'autos/' + self.filename + '.txt', "MASAscript (*.txt)")[0]
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
