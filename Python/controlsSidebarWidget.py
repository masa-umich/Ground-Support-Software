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
        self.height = self.parent.height
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
    """
    Simple tab widget that can hold whatever is nice to display in bottom right
    """

    def __init__(self, parent):

        super().__init__(parent)

        self.controlsSidebarWidget = parent
        self.gui = self.controlsSidebarWidget.gui

        self.setFixedHeight(int(415 * self.gui.pixel_scale_ratio[1]))
        self.setFixedWidth(self.controlsSidebarWidget.width)

        self.tabWidget = QTabWidget(self)
        self.tabWidget.setFixedWidth(self.width())
        self.tabWidget.setFixedHeight(self.height())

        # create widgets
        self.noteWidget = SidebarNoteWidget(self.tabWidget, self.controlsSidebarWidget)
        self.packetLogWidget = SidebarPacketLogWidget(self.tabWidget, self.controlsSidebarWidget)

        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tab5 = QWidget()
        self.tab6 = QWidget()

        # add in tabs with widgets
        self.tabWidget.addTab(self.noteWidget, "Notes")
        self.tabWidget.addTab(self.packetLogWidget, "Packet Log")
        #self.tabWidget.addTab(self.controlsSidebarWidget.window.limits.widget, "Limits")
        # self.tabWidget.addTab(self.tab3, "Packet Log2")
        # self.tabWidget.addTab(self.tab4, "Packet Log3")
        # self.tabWidget.addTab(self.tab5, "Packet Log4")
        # self.tabWidget.addTab(self.tab6, "Packet Log5")

        self.show()


class SidebarPacketLogWidget(QWidget):
    """
    Adds in the equivalent of the server side packet log. This is designed to go in the tab widget in the sidebar.
    This packet log has the advantage of being filterable so users can quickly find what they are looking for
    """

    def __init__(self, tabWidget, sideBar=None):

        super().__init__()

        self.gui = sideBar.gui
        self.tabWidget = tabWidget
        self.controlsSidebarWidget = sideBar
        self.interface = self.controlsSidebarWidget.window.interface

        # holds the all the widgets
        self.vertLayout = QVBoxLayout()

        # holds the filter buttons
        self.filterHLayout = QHBoxLayout()

        # setup the packet log, lot of shenanigans to make things fit and look good
        self.packet_log = QTableWidget(self)
        self.packet_log.setColumnCount(3)
        self.packet_log.setHorizontalHeaderLabels(["Channel", "Value", "Unit"])
        self.packet_log.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.packet_log.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.packet_log.setColumnWidth(0, self.controlsSidebarWidget.width * .57 - 34 * self.gui.pixel_scale_ratio[0])
        self.packet_log.setColumnWidth(1, self.controlsSidebarWidget.width * .25)
        self.packet_log.setColumnWidth(2, self.controlsSidebarWidget.width * .18)
        self.packet_log.verticalHeader().hide()

        # Board filter, tool buttons are a special button that act like menu items
        self.boardFilterButton = QToolButton(self)
        self.boardFilterButton.setText("Board Filter")
        self.boardtoolmenu = QMenu(self)
        self.boardFilterList = []  # Holds board names that we want to filter by. Defualt all (added later)

        # type filter, tool buttons are a special button that act like menu items
        self.typeFilterButton = QToolButton(self)
        self.typeFilterButton.setText("Type Filter")
        self.typetoolmenu = QMenu(self)
        self.typeFilterList = ["other", "pressure", "vlv", "mtr", "STATE", "load", "tc", "rtd", "tnk", "ctrl_press",
                               "cal"]  # Holds type names that we want to filter by. Defualt all

        self.filteredChannels = []  # populated later

        # I stole this from a stackoverflow post that I can't find again. Adds checkbox to combobox basically
        # also this is where the function callbacks are
        for boardName in Constants.boards:
            checkBox = QCheckBox(boardName, self.boardtoolmenu)
            checkBox.stateChanged.connect(self.boardFilterButtonUpdated)
            checkBox.setChecked(True)
            checkableAction = QWidgetAction(self.boardtoolmenu)
            checkableAction.setDefaultWidget(checkBox)
            self.boardtoolmenu.addAction(checkableAction)

        self.boardFilterButton.setMenu(self.boardtoolmenu)
        self.boardFilterButton.setPopupMode(QToolButton.InstantPopup)

        # type filter setup, same as above board
        for typeName in self.typeFilterList:
            checkBox = QCheckBox(typeName, self.typetoolmenu)
            checkBox.setChecked(True)
            checkBox.stateChanged.connect(self.typeFilterButtonUpdated)
            checkableAction = QWidgetAction(self.typetoolmenu)
            checkableAction.setDefaultWidget(checkBox)
            self.typetoolmenu.addAction(checkableAction)

        self.typeFilterButton.setMenu(self.typetoolmenu)
        self.typeFilterButton.setPopupMode(QToolButton.InstantPopup)
        self.typeFilterButton.installEventFilter(self)
        self.boardFilterButton.installEventFilter(self)

        self.filterHLayout.addWidget(self.boardFilterButton)
        self.filterHLayout.addWidget(self.typeFilterButton)

        self.gui.liveDataHandler.dataPacketSignal.connect(self.updateFromDataPacket)

        self.vertLayout.addLayout(self.filterHLayout)
        self.vertLayout.addWidget(self.packet_log)
        self.setLayout(self.vertLayout)

    @overrides
    def eventFilter(self, source, event: QEvent):
        """
        Need an event filter to prevent the tool button from causing the status bar to disapear
        :param source: the self.blahh of whatever is sending the signal
        :param event: the event triggered
        :return: True for preventing the event to handled again later downstream
        """
        if (source is self.typeFilterButton or source is self.boardFilterButton) and event.type() == QEvent.StatusTip:
            return True  # Returning true will prevent this event from being processed again down the line

        return super().eventFilter(source, event)

    def boardFilterButtonUpdated(self, state):
        """
        Called from board menu callback. When called it updates the filter list and table
        :param state: state of the menu checkbox clicked. 2 = checked
        :return: none
        """
        board = self.sender().text()
        if state == 2:
            self.boardFilterList.append(self.controlsSidebarWidget.interface.getPrefix(board))
        else:
            self.boardFilterList.remove(self.controlsSidebarWidget.interface.getPrefix(board))

        self.populatePacketLogFromFilter()

    def typeFilterButtonUpdated(self, state):
        """
        Called from type menu callback. When called it updates the filter list and table
        :param state: state of the menu checkbox clicked. 2 = checked
        :return: none
        """
        type = self.sender().text()
        if state == 2:
            self.typeFilterList.append(type)
        else:
            self.typeFilterList.remove(type)

        self.populatePacketLogFromFilter()

    # TODO: Gets once for every board on startup which is probably not great
    def populatePacketLogFromFilter(self):
        """
        This function is called when the filter is updated. When updated, this compiles a list of all channels that
        comply with the filter. It then updates the table to show those items
        :return: none
        """

        # Get all the channels and then first filter by board
        allChannels = self.controlsSidebarWidget.interface.channels
        boardfilteredChannels = [x for x in allChannels if any(y in x for y in self.boardFilterList)]

        # Other is used to represent items that don't fit into the filter. Other channels need to be filtered
        # alone because the other filters will always remove them
        if "other" in self.typeFilterList:
            otherChannels = [x for x in boardfilteredChannels if all(y not in x for y in self.typeFilterList)]
        else:
            otherChannels = []

        # from the board filtered list, then filter by the type filters
        filteredChannels = [x for x in boardfilteredChannels if any(y in x for y in self.typeFilterList)]

        # TODO: Try to preserve the given order, not just thrown at the end
        self.filteredChannels = filteredChannels + otherChannels

        # Update the table, need ot clear, set the rows, then for each item add it to the table, row num, value, units
        self.clearTable()
        self.packet_log.setRowCount(len(filteredChannels))
        for n in range(len(filteredChannels)):
            item = QTableWidgetItem(filteredChannels[n])
            self.packet_log.setItem(
                n, 0, item)
            item = QTableWidgetItem("", 1)
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.packet_log.setItem(n, 1, item)
            self.packet_log.setItem(n, 2, QTableWidgetItem(
                self.interface.units[filteredChannels[n]]))

    def clearTable(self):
        """
        Clears the whole tables
        :return: none
        """

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
        self.noteBox.setColumnWidth(1, math.floor(self.tabWidget.width() * .65)-40*self.gui.pixel_scale_ratio[0])
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
