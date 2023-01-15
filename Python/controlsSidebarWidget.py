from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants
from board import Board
from packetLogWidget import PacketLogWidget

import math
import random

from overrides import overrides


class ControlsSidebarWidget(QWidget):
    """
    Widget that contains relevant information while conducting a test
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.centralWidget = parent
        self.window = parent.window
        self.controlsWidget = self.centralWidget.controlsWidget
        self.gui = self.centralWidget.gui
        self.interface = self.window.interface

        # Defines placement and size of control panel
        self.left = self.gui.screenResolution[0] - self.centralWidget.panel_width
        self.top = 0

        self.width = self.centralWidget.panel_width
        self.height = self.parent.height
        self.setGeometry(int(self.left), int(self.top), int(self.width), int(self.height))

        # Sets color of control panel
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Constants.MASA_Blue_color)
        self.setPalette(p)

        self.painter = QPainter()

        self.show()
        self.noteBoxText = "CET - 00:00:00"

        # Create the label that will hold the status label, displays what task is being performed
        title_font = QFont()
        title_font.setStyleStrategy(QFont.PreferAntialias)
        title_font.setFamily(Constants.monospace_font)
        title_font.setPointSizeF(48 * self.gui.font_scale_ratio)
        title_font.setHintingPreference(QFont.PreferNoHinting)
        self.title_label = QLabel(self)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: white")
        self.title_label.setText("Avionics")
        self.title_label.setFixedHeight(int(75 * self.gui.pixel_scale_ratio[1]))
        self.title_label.setFixedWidth(int(self.width))
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title_label.move(int(10 * self.gui.pixel_scale_ratio[0]), 0)  # Nasty but makes it look more centered
        self.title_label.show()

        time_font = QFont()
        time_font.setStyleStrategy(QFont.PreferAntialias)
        time_font.setFamily(Constants.default_font)
        time_font.setPointSize(30 * self.gui.font_scale_ratio)

        # self.state_time_label = QLabel(self)
        # self.state_time_label = QLabel(self)
        # self.state_time_label.setFont(time_font)
        # self.state_time_label.setStyleSheet("color: white")
        # self.state_time_label.setText("Rem Time: 00 s")
        # self.state_time_label.setFixedHeight(75 * self.gui.pixel_scale_ratio[1])
        # self.state_time_label.setFixedWidth(self.width)
        # self.state_time_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # self.state_time_label.move(10 * self.gui.pixel_scale_ratio[0], 85 * self.gui.pixel_scale_ratio[1])  # Nasty but makes it look more centered
        # self.state_time_label.show()

        self.tabWidget = SidebarTabWidget(self)
        self.tabWidget.move(3, int(self.height - self.tabWidget.height() + 3 * self.gui.pixel_scale_ratio[1]))
        self.tabWidget.show()

        self.board_objects = []  # An empty array to start

        # Scroll Bar Layout
        self.scroll = QScrollArea(self)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollAreaLayout = QVBoxLayout()
        self.scrollAreaLayout.setAlignment(Qt.AlignTop)
        self.scrollAreaLayoutBox = QWidget()
        self.scrollAreaLayoutBox.setLayout(self.scrollAreaLayout)
        self.scroll.setWidget(self.scrollAreaLayoutBox)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setFixedWidth(int(self.parent.panel_width - 2))
        self.scroll.move(2, int(self.title_label.pos().y() + self.title_label.height() + 15 * self.gui.pixel_scale_ratio[1]))
        self.scroll.setFixedHeight(self.tabWidget.y() - self.scroll.pos().y())
        self.scroll.show()

    def addBoardsToScrollWidget(self, boardNames: [], silent = False):
        """
        Add in boards to be shown on the sidebar. Only need to pass in the name
        :param boardNames: A list of board names that needs to be passed
        :param silent: boolean, for a really dirty fix when leaving edit mode
        """

        # Reset Layout
        for i in reversed(range(self.scrollAreaLayout.count())):
            self.scrollAreaLayout.itemAt(i).widget().deleteLater()

        for board in self.board_objects:
            board.deleteLater()
            board = None
            del board
        self.board_objects.clear()

        # Add in all the boards, update the next position to insert them
        for name in boardNames:
            board = Board(self, name)
            self.scrollAreaLayout.addWidget(board)
            self.board_objects.append(board)

        # We occasionally need to call this function to update boards at weird times, we don't want the status bar when
        # that happens
        if not silent:
            self.gui.setStatusBarMessage("Boards: " + str(boardNames) + " added")

    '''def addBoards(self, boardNames: []):
        """
        Add in boards to be shown on the sidebar. Only need to pass in the name
        :param boardNames: A list of board names that needs to be passed
        """
        y_pos = (150 * self.gui.pixel_scale_ratio[1] + 1) + self.noteBox_height

        # Delete all the current shown boards, if any
        # TODO: Make this feel better because this is a lazy way to do it
        for board in self.board_objects:
            board.deleteLater()
            board = None
            del board
        self.board_objects.clear()

        # Add in all the boards, update the next position to insert them
        for name in boardNames:
            board = Board(self, name)
            board.move(2, y_pos)
            self.board_objects.append(board)
            y_pos = board.pos().y() + board.height()

        self.window.setStatusBarMessage("Boards: " + str(boardNames) + " added")'''

    def abort_init(self):
        """Changes the state of each board. 
        """
        self.gui.setStatusBarMessage("Abort button clicked!")
        if self.board_objects:
            for board in self.board_objects:
                if board.name == "Pressurization Controller" or board.name == "Engine Controller":
                    board.sendBoardState("Abort")

    @overrides
    def paintEvent(self, e):
        """
        This event is called automatically in the background by pyQt. It is used to update the drawing on screen
        This function calls the objects own drawing methods to perform the actual drawing calculations
        """
        self.painter.begin(self)

        # This makes the objects onscreen more crisp
        self.painter.setRenderHint(QPainter.HighQualityAntialiasing)

        # Default pen qualities
        pen = QPen()
        pen.setWidth(Constants.line_width)
        pen.setColor(Constants.MASA_Beige_color)
        self.painter.setPen(pen)

        # Draw the bottom border on the widget
        path = QPainterPath()
        # path.moveTo(0, 75 * self.gui.pixel_scale_ratio[1]-1)  # Bottom left corner
        # path.lineTo(self.width, 75 * self.gui.pixel_scale_ratio[1]-1)  # Straight across

        path.moveTo(1, 0)
        path.lineTo(1, self.height)
        path.moveTo(1, 85 * self.gui.pixel_scale_ratio[1]-1)
        path.lineTo(self.width, 85 * self.gui.pixel_scale_ratio[1]-1)

        self.painter.drawPath(path)

        self.painter.end()

    def generateSaveDict(self):
        """
        Generates the save dict for the boards
        :return save_dict: returns the save dictionary
        """
        save_dict = {}
        for i, board in enumerate(self.board_objects):
            save_dict["Board "+str(i)] = board.name

        return save_dict


class SidebarTabWidget(QWidget):
    """
    Simple tab widget that can hold whatever is nice to display in bottom right
    """

    def __init__(self, parent):

        super().__init__(parent)

        self.controlsSidebarWidget = parent
        self.gui = self.controlsSidebarWidget.gui

        self.setFixedHeight(int(415 * self.gui.pixel_scale_ratio[1]))
        self.setFixedWidth(int(self.controlsSidebarWidget.width))

        self.tabWidget = QTabWidget(self)
        self.tabWidget.setFixedWidth(self.width())
        self.tabWidget.setFixedHeight(self.height())

        # create widgets
        self.noteWidget = SidebarNoteWidget(self.tabWidget, self.controlsSidebarWidget)
        self.packetLogWidget = PacketLogWidget(self.tabWidget, self.controlsSidebarWidget.window.interface, self.gui.liveDataHandler.dataPacketSignal)
        # SidebarPacketLogWidget(self.tabWidget, self.controlsSidebarWidget)

        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tab5 = QWidget()
        self.tab6 = QWidget()

        # add in tabs with widgets
        self.tabWidget.addTab(self.noteWidget, "Notes")
        self.tabWidget.addTab(self.packetLogWidget, "Packet Log")
        # self.tabWidget.addTab(self.controlsSidebarWidget.window.limits.widget, "Limits")
        # self.tabWidget.addTab(self.tab3, "Packet Log2")
        # self.tabWidget.addTab(self.tab4, "Packet Log3")
        # self.tabWidget.addTab(self.tab5, "Packet Log4")
        # self.tabWidget.addTab(self.tab6, "Packet Log5")

        self.show()


class SidebarNoteWidget(QWidget):
    """
    This class is a wrapper for a custom note widget. It allows for single line entry of notes. Once entered the notes
    are displayed in a nice looking grid with a timestamp. Currently only meant to be used in the tab bar but can very
    easily be used as its own widget
    """

    def __init__(self, tabWidget,  sideBar):

        super().__init__()

        self.tabWidget = tabWidget
        self.controlsSidebarWidget = sideBar

        self.gui = self.controlsSidebarWidget.gui

        # Only want notes to be allowed when connected with the server
        self.gui.campaign.campaignStartSignal.connect(self.enableNoteCreation)
        self.gui.campaign.campaignEndSignal.connect(self.disableNoteCreation)

        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.monospace_font)

        # layout to hold all the widgets
        self.vlayout = QVBoxLayout()

        # widget where notes are displayed
        self.noteBox = QTableWidget(self)
        font.setPointSize(12 * self.gui.font_scale_ratio)

        self.vlayout.addWidget(self.noteBox)

        # set up notebox to be perty
        self.noteBox.setColumnCount(2)
        self.noteBox.setRowCount(0)
        # This is kinda a mess, need to set the width so things can fit. Can't use all the space because then starts to
        # clip weirdly so this was easiest
        self.noteBox.setColumnWidth(0, math.floor(self.tabWidget.width() * .35))
        self.noteBox.setColumnWidth(1, int(math.floor(self.tabWidget.width() * .65)-40*self.gui.pixel_scale_ratio[0]))
        self.noteBox.horizontalHeader().hide()
        self.noteBox.verticalHeader().hide()

        # Some settings here to prevent editing and clicking
        self.noteBox.setShowGrid(False)
        self.noteBox.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.noteBox.setFocusPolicy(Qt.NoFocus)
        self.noteBox.setSelectionMode(QAbstractItemView.NoSelection)
        self.noteBox.resizeRowsToContents()

        self.noteBox.show()

        # line edit is where the user can type in notes
        self.lineEdit = QLineEdit(self)
        self.lineEdit.returnPressed.connect(self.enterNewNote)
        self.lineEdit.setPlaceholderText("Start campaign for notes")
        self.lineEdit.setDisabled(True)
        self.lineEdit.show()
        self.lineEdit.clearFocus()

        self.vlayout.addWidget(self.lineEdit)

        self.setLayout(self.vlayout)

    def enterNewNote(self):
        """
        This is the function connected to the line edit where users type in notes. When a note is entered then it is
        added to the table view and sent to the server
        :return: none
        """

        # don't sent blank notes
        if self.lineEdit.text() == "":
            return

        # add row for note to be displayed
        self.noteBox.setRowCount(self.noteBox.rowCount()+1)

        cetString = self.gui.controlsWindow.centralWidget.missionWidget.generateCETAsText(self.gui.campaign.CET)

        # add in both items to the table. Need to use the below class, the flags prevent them from being edited.
        item = QTableWidgetItem(cetString)
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        item.setTextAlignment(Qt.AlignTop)
        self.noteBox.setItem(self.noteBox.rowCount()-1, 0, item)

        item = QTableWidgetItem(self.lineEdit.text())
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        item.setTextAlignment(Qt.AlignTop)
        self.noteBox.setItem(self.noteBox.rowCount()-1, 1, item)

        self.noteBox.resizeRowsToContents()

        self.noteBox.scrollToBottom()

        # send command to server
        self.gui.liveDataHandler.sendCommand(9, [cetString,  "NOTE", self.lineEdit.text()])

        self.clearFocus()

        self.lineEdit.clear()

    def enableNoteCreation(self):
        """
        Function that is connected to the campaignStartSignal
        :return: none
        """

        self.lineEdit.setEnabled(True)
        self.lineEdit.setPlaceholderText("Enter note here")

    def disableNoteCreation(self, noServer:bool = False):
        """
        Function that is connected to the campaignEndSignal. Can be called directly when server connection is lost to
        display that no server is connected
        :param noServer: is true when the gui has no active server connection
        :return: none
        """

        self.lineEdit.setDisabled(True)
        if noServer and self.gui.campaign.is_active:
            self.lineEdit.setPlaceholderText("Reconnect to server for notes")
        else:
            self.lineEdit.setPlaceholderText("Start campaign for notes")
