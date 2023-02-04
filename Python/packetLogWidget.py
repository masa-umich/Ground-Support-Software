from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants

from overrides import overrides


class PacketLogWidget(QWidget):
    """
    Packet log that has filter options. This is designed to go in both the console and server.
    This packet log has the advantage of being filterable so users can quickly find what they are looking for
    """

    def __init__(
        self,
        tabWidget,
        interface,
        data_update_signal: pyqtSignal,
        autoresize_cols: bool = False,
    ):

        super().__init__()

        # TODO: This is designed to go in a tab (helps with performance. If this wants to be removed it is easy, just change this to be parent(I think))
        self.tabWidget = tabWidget
        self.interface = interface
        data_update_signal.connect(self.updateFromDataPacket)

        # holds the all the widgets
        self.vertLayout = QVBoxLayout()

        # holds the filter buttons
        self.filterHLayout = QHBoxLayout()

        # setup the packet log, lot of shenanigans to make things fit and look good
        self.packet_log = QTableWidget(self)
        self.packet_log.setColumnCount(3)
        self.packet_log.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.packet_log.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        if not autoresize_cols:
            self.packet_log.setColumnWidth(0, int(self.tabWidget.width() * 0.45))
            self.packet_log.setColumnWidth(1, int(self.tabWidget.width() * 0.25))
            self.packet_log.setColumnWidth(2, int(self.tabWidget.width() * 0.18))
        else:
            header = self.packet_log.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.packet_log.verticalHeader().hide()

        self.packet_log.setHorizontalHeaderLabels(["Channel", "Value", "Unit"])

        # Board filter, tool buttons are a special button that act like menu items
        self.boardFilterButton = QToolButton(self)
        self.boardFilterButton.setMinimumWidth(int(self.tabWidget.width() * 0.25))
        self.boardFilterButton.setText("Board Filter")
        self.boardtoolmenu = QMenu(self)
        self.boardFilterList = [
            "GSE Controller",
            "Engine Controller",
        ]  # Holds board names that we want to filter by. Defualt some

        # type filter, tool buttons are a special button that act like menu items
        self.typeFilterButton = QToolButton(self)
        self.typeFilterButton.setMinimumWidth(int(self.tabWidget.width() * 0.25))
        self.typeFilterButton.setText("Type Filter")
        self.typetoolmenu = QMenu(self)
        self.typeFilterList_STATIC = [
            "other",
            "pressure",
            "vlv",
            "mtr",
            "STATE",
            "load",
            "tc",
            "rtd",
            "tnk",
            "ctrl_press",
            "cal",
        ]  # will always have this values, below list changes with user selection
        self.typeFilterList = [
            "pressure",
            "vlv",
            "STATE",
        ]  # Holds type names that we want to filter by. Defualt some

        self.filteredChannels = []  # populated later

        # I stole this from a stackoverflow post that I can't find again. Adds checkbox to combobox basically
        # also this is where the function callbacks are
        for boardName in Constants.boards:
            checkBox = QCheckBox(boardName, self.boardtoolmenu)
            checkBox.stateChanged.connect(self.boardFilterButtonUpdated)
            if boardName in self.boardFilterList:
                checkBox.setChecked(True)
            checkableAction = QWidgetAction(self.boardtoolmenu)
            checkableAction.setDefaultWidget(checkBox)
            self.boardtoolmenu.addAction(checkableAction)

        self.boardFilterButton.setMenu(self.boardtoolmenu)
        self.boardFilterButton.setPopupMode(QToolButton.InstantPopup)

        # type filter setup, same as above board
        for typeName in self.typeFilterList_STATIC:
            checkBox = QCheckBox(typeName, self.typetoolmenu)
            if typeName in self.typeFilterList:
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

        self.vertLayout.addLayout(self.filterHLayout)
        self.vertLayout.addWidget(self.packet_log)
        self.setLayout(self.vertLayout)

    @overrides
    def eventFilter(self, source, event: QEvent):
        """
        Need an event filter to prevent the tool button from causing the status bar to disappear
        :param source: the self.blahh of whatever is sending the signal
        :param event: the event triggered
        :return: True for preventing the event to handled again later downstream
        """
        if (
            source is self.typeFilterButton or source is self.boardFilterButton
        ) and event.type() == QEvent.StatusTip:
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
            self.boardFilterList.append(self.interface.getPrefix(board))
        else:
            self.boardFilterList.remove(self.interface.getPrefix(board))

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
        allChannels = self.interface.channels
        boardfilteredChannels = [
            x for x in allChannels if any(y in x for y in self.boardFilterList)
        ]

        # Other is used to represent items that don't fit into the filter. Other channels need to be filtered
        # alone because the other filters will always remove them
        if "other" in self.typeFilterList:
            otherChannels = [
                x
                for x in boardfilteredChannels
                if all(y not in x for y in self.typeFilterList_STATIC)
            ]
        else:
            otherChannels = []

        # from the board filtered list, then filter by the type filters
        filteredChannels = [
            x for x in boardfilteredChannels if any(y in x for y in self.typeFilterList)
        ]

        # TODO: Try to preserve the given order, not just thrown at the end
        self.filteredChannels = filteredChannels + otherChannels

        # Update the table, need ot clear, set the rows, then for each item add it to the table, row num, value, units
        self.clearTable()
        self.packet_log.setRowCount(len(self.filteredChannels))
        for n in range(len(self.filteredChannels)):
            item = QTableWidgetItem(self.filteredChannels[n])
            self.packet_log.setItem(n, 0, item)
            item = QTableWidgetItem("", 1)
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.packet_log.setItem(n, 1, item)
            self.packet_log.setItem(
                n, 2, QTableWidgetItem(self.interface.units[self.filteredChannels[n]])
            )

        self.packet_log.setHorizontalHeaderLabels(["Channel", "Value", "Unit"])

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
