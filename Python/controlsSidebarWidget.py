from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants
from board import Board

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
        self.height = self.gui.screenResolution[1] - self.parent.status_bar_height
        self.setGeometry(self.left, self.top, self.width, self.height)

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
        self.title_label.setFixedHeight(75 * self.gui.pixel_scale_ratio[1])
        self.title_label.setFixedWidth(self.width)
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title_label.move(10 * self.gui.pixel_scale_ratio[0], 0)  # Nasty but makes it look more centered
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
        self.tabWidget.move(3, self.height - self.tabWidget.height() + 3 * self.gui.pixel_scale_ratio[1])
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
        self.scroll.setFixedWidth(self.parent.panel_width - 2)
        self.scroll.move(2, self.title_label.pos().y() + self.title_label.height() + 15 * self.gui.pixel_scale_ratio[1])
        self.scroll.setFixedHeight(self.tabWidget.y() - self.scroll.pos().y())
        self.scroll.show()

    def addBoardsToScrollWidget(self, boardNames: []):
        """
        Add in boards to be shown on the sidebar. Only need to pass in the name
        :param boardNames: A list of board names that needs to be passed
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

        self.window.statusBar().showMessage("Boards: " + str(boardNames) + " added")

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

        self.window.statusBar().showMessage("Boards: " + str(boardNames) + " added")'''

    def abort_init(self):
        """Changes the state of each board. 
        """
        self.window.statusBar().showMessage("Abort button clicked!")
        if self.board_objects:
            for board in self.board_objects:
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

    def __init__(self, parent):

        super().__init__(parent)

        self.controlsSidebarWidget = parent
        self.gui = self.controlsSidebarWidget.gui

        self.setFixedHeight(int(415 * self.gui.pixel_scale_ratio[1]))
        self.setFixedWidth(self.controlsSidebarWidget.width)

        self.tabWidget = QTabWidget(self)
        self.tabWidget.setFixedWidth(self.width())
        self.tabWidget.setFixedHeight(self.height())

        self.noteWidget = SidebarNoteWidget(self.tabWidget, self.controlsSidebarWidget)
        self.packetLogWidget = SidebarPacketLogWidget(self.tabWidget, self.controlsSidebarWidget)

        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tab5 = QWidget()
        self.tab6 = QWidget()

        self.tabWidget.addTab(self.noteWidget, "Notes")
        self.tabWidget.addTab(self.packetLogWidget, "Packet Log")
        #self.tabWidget.addTab(self.controlsSidebarWidget.window.limits.widget, "Limits")
        # self.tabWidget.addTab(self.tab3, "Packet Log2")
        # self.tabWidget.addTab(self.tab4, "Packet Log3")
        # self.tabWidget.addTab(self.tab5, "Packet Log4")
        # self.tabWidget.addTab(self.tab6, "Packet Log5")

        self.show()


class SidebarPacketLogWidget(QWidget):

    def __init__(self, tabWidget, sideBar=None):

        super().__init__()

        self.gui = sideBar.gui
        self.tabWidget = tabWidget
        self.controlsSidebarWidget = sideBar
        self.interface = self.controlsSidebarWidget.window.interface

        self.vertLayout = QVBoxLayout()

        self.filterHLayout = QHBoxLayout()

        self.packet_log = QTableWidget(self)
        self.packet_log.setColumnCount(3)
        self.packet_log.setHorizontalHeaderLabels(["Channel", "Value", "Unit"])
        self.packet_log.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.packet_log.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.packet_log.setColumnWidth(0, self.controlsSidebarWidget.width * .57 - 34 * self.gui.pixel_scale_ratio[0])
        self.packet_log.setColumnWidth(1, self.controlsSidebarWidget.width * .25)
        self.packet_log.setColumnWidth(2, self.controlsSidebarWidget.width * .18)
        self.packet_log.verticalHeader().hide()

        self.boardFilterButton = QToolButton(self)
        self.boardFilterButton.setText("Board Filter")
        self.boardtoolmenu = QMenu(self)
        self.boardFilterList = []  # Holds board names that we want to filter by. Defualt all

        self.typeFilterButton = QToolButton(self)
        self.typeFilterButton.setText("Type Filter")
        self.typetoolmenu = QMenu(self)
        self.typeFilterList = ["other", "pressure", "vlv", "mtr", "STATE", "load", "tc", "rtd", "tnk", "ctrl_press",
                               "cal"]  # Holds type names that we want to filter by. Defualt all

        self.filteredChannels = []  # populated later

        # board filter setup
        for boardName in Constants.boards:
            checkBox = QCheckBox(boardName, self.boardtoolmenu)
            checkBox.stateChanged.connect(self.boardFilterButtonUpdated)
            checkBox.setChecked(True)
            checkableAction = QWidgetAction(self.boardtoolmenu)
            checkableAction.setDefaultWidget(checkBox)
            self.boardtoolmenu.addAction(checkableAction)

        self.boardFilterButton.setMenu(self.boardtoolmenu)
        self.boardFilterButton.setPopupMode(QToolButton.InstantPopup)

        # type filter setup
        for typeName in self.typeFilterList:
            checkBox = QCheckBox(typeName, self.typetoolmenu)
            checkBox.setChecked(True)
            checkBox.stateChanged.connect(self.typeFilterButtonUpdated)
            checkableAction = QWidgetAction(self.typetoolmenu)
            checkableAction.setDefaultWidget(checkBox)
            self.typetoolmenu.addAction(checkableAction)

        self.typeFilterButton.setMenu(self.typetoolmenu)
        self.typeFilterButton.setPopupMode(QToolButton.InstantPopup)

        self.filterHLayout.addWidget(self.boardFilterButton)
        self.filterHLayout.addWidget(self.typeFilterButton)

        self.gui.liveDataHandler.dataPacketSignal.connect(self.updateFromDataPacket)

        self.vertLayout.addLayout(self.filterHLayout)
        self.vertLayout.addWidget(self.packet_log)
        self.setLayout(self.vertLayout)
        # self.packet_log.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # self.packet_log.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        # self.packet_log.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

    def boardFilterButtonUpdated(self, state):
        board = self.sender().text()
        if state == 2:
            self.boardFilterList.append(self.controlsSidebarWidget.interface.getPrefix(board))
        else:
            self.boardFilterList.remove(self.controlsSidebarWidget.interface.getPrefix(board))

        self.populatePacketLogFromFilter()

    def typeFilterButtonUpdated(self, state):
        type = self.sender().text()
        if state == 2:
            self.typeFilterList.append(type)
        else:
            self.typeFilterList.remove(type)

        self.populatePacketLogFromFilter()

    # TODO: Gets once for every board on startup which is probably not great
    def populatePacketLogFromFilter(self):
        allChannels = self.controlsSidebarWidget.interface.channels
        boardfilteredChannels = [x for x in allChannels if any(y in x for y in self.boardFilterList)]

        if "other" in self.typeFilterList:
            otherChannels = [x for x in boardfilteredChannels if all(y not in x for y in self.typeFilterList)]
        else:
            otherChannels = []

        filteredChannels = [x for x in boardfilteredChannels if any(y in x for y in self.typeFilterList)]

        # TODO: Try to preserve the given order, not just thrown at the end
        self.filteredChannels = filteredChannels + otherChannels

        self.clearTable()
        self.packet_log.setRowCount(len(filteredChannels))
        for n in range(len(filteredChannels)):
            item = QTableWidgetItem(filteredChannels[n])
            self.packet_log.setItem(
                n, 0, item)
            item = QTableWidgetItem(str(round(random.random() * 6000, 1)))
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.packet_log.setItem(n, 1, item)
            self.packet_log.setItem(n, 2, QTableWidgetItem(
                self.interface.units[filteredChannels[n]]))

    def clearTable(self):

        self.packet_log.clear()
        self.packet_log.setRowCount(0)

    @pyqtSlot(object)
    def updateFromDataPacket(self, data_packet: dict):
        """
        Update the data in the packet log
        :param data_packet: data packet from the livedatahandler
        """

        # We only want to update this if we are looking at the tab
        if self.tabWidget.tabText(self.tabWidget.currentIndex()) == "Packet Log":
            for n in range(len(self.filteredChannels)):
                key = self.filteredChannels[n]
                item = QTableWidgetItem(str(round(data_packet[key], 1)))
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                self.packet_log.setItem(n, 1, item)


class SidebarNoteWidget(QWidget):

    # TODO: Cleanup this sections, kinda confusing on what all the parent and sidebar shit is
    def __init__(self, parent,  sideBar = None):

        super().__init__()

        self.parent = parent
        if sideBar is None:
            self.controlsSidebarWidget = parent
        else:
            self.controlsSidebarWidget = sideBar

        self.gui = self.controlsSidebarWidget.gui

        self.gui.campaign.campaignStartSignal.connect(self.enableNoteCreation)
        self.gui.campaign.campaignEndSignal.connect(self.disableNoteCreation)

        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.monospace_font)

        self.vlayout = QVBoxLayout()

        self.noteBox = QTableWidget(self)
        font.setPointSize(12 * self.gui.font_scale_ratio)

        self.vlayout.addWidget(self.noteBox)

        self.noteBox.setColumnCount(2)
        self.noteBox.setRowCount(2)
        self.noteBox.setColumnWidth(0, math.floor(self.parent.width() * .35))
        self.noteBox.setColumnWidth(1, math.floor(self.parent.width() * .65)-40*self.gui.pixel_scale_ratio[0])
        self.noteBox.horizontalHeader().hide()
        self.noteBox.verticalHeader().hide()

        self.noteBox.setStyleSheet("QTableView::item { border:0px; padding: 2px;}")
        item = QTableWidgetItem("CET-00:00:00")
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        item.setTextAlignment(Qt.AlignTop)
        self.noteBox.setItem(0, 0, item)

        item = QTableWidgetItem("Test Note that is short")
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        item.setTextAlignment(Qt.AlignTop)
        item.setBackground(Constants.MASA_Blue_color)
        self.noteBox.setItem(0, 1, item)

        item = QTableWidgetItem("CET-00:00:00")
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        item.setTextAlignment(Qt.AlignTop)
        item.setBackground(Constants.MASA_Blue_color)
        self.noteBox.setItem(1, 0, item)

        item = QTableWidgetItem("Test Note that is reallllllllly long and that hahaha omg tube bends")
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        item.setTextAlignment(Qt.AlignTop)
        item.setBackground(Constants.MASA_Blue_color)
        self.noteBox.setItem(1, 1, item)
        self.noteBox.setShowGrid(False)

        self.noteBox.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.noteBox.setFocusPolicy(Qt.NoFocus)
        self.noteBox.setSelectionMode(QAbstractItemView.NoSelection)
        self.noteBox.resizeRowsToContents()

        self.noteBox.show()

        self.lineEdit = QLineEdit(self)
        self.lineEdit.returnPressed.connect(self.enterNewNote)
        self.lineEdit.setPlaceholderText("Start campaign for notes")
        self.lineEdit.setDisabled(True)
        self.lineEdit.show()
        self.lineEdit.clearFocus()

        self.vlayout.addWidget(self.lineEdit)

        self.setLayout(self.vlayout)

    def enterNewNote(self):

        if self.lineEdit.text() == "":
            return

        self.noteBox.setRowCount(self.noteBox.rowCount()+1)

        cetString = self.gui.controlsWindow.centralWidget.missionWidget.generateCETAsText(self.gui.campaign.CET)

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

        self.clearFocus()

        self.lineEdit.clear()

    def enableNoteCreation(self):

        self.lineEdit.setEnabled(True)
        self.lineEdit.setPlaceholderText("Enter note here")

    def disableNoteCreation(self, noServer:bool = False):

        self.lineEdit.setDisabled(True)
        if noServer and self.gui.campaign.is_active:
            self.lineEdit.setPlaceholderText("Reconnect to server for notes")
        else:
            self.lineEdit.setPlaceholderText("Start campaign for notes")
