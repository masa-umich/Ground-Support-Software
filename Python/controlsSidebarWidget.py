from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants
from board import Board

import math

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

        self.state_time_label = QLabel(self)
        self.state_time_label = QLabel(self)
        self.state_time_label.setFont(time_font)
        self.state_time_label.setStyleSheet("color: white")
        self.state_time_label.setText("Rem Time: 00 s")
        self.state_time_label.setFixedHeight(75 * self.gui.pixel_scale_ratio[1])
        self.state_time_label.setFixedWidth(self.width)
        self.state_time_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.state_time_label.move(10 * self.gui.pixel_scale_ratio[0], 85 * self.gui.pixel_scale_ratio[1])  # Nasty but makes it look more centered
        self.state_time_label.show()

        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.default_font)
        font.setPointSize(12 * self.gui.font_scale_ratio)

        # self.noteBox = QTextEdit(self)
        # self.noteBox.setReadOnly(True)
        # self.noteBox.setFont(font)
        # self.noteBox.setFixedWidth(self.width - 15)
        # self.noteBox_height = int(self.width/3)
        # self.noteBox.setFixedHeight(self.noteBox_height)
        # self.noteBox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # self.noteBox.move(10, 160 * self.gui.pixel_scale_ratio[1])
        # self.noteBox.setText(self.noteBoxText)
        # self.noteBox.show()

        self.tabWidget = SidebarTabWidget(self)
        self.tabWidget.move(3, 160 * self.gui.pixel_scale_ratio[1])

        self.state_frame = QFrame(self)
        self.state_frame.setGeometry(self.left, 0, self.width*3, 80 * self.gui.pixel_scale_ratio[1])

        # Vertical button layout
        self.buttonLayout = QVBoxLayout(self.state_frame)
        self.setLayout(self.buttonLayout)

        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.default_font)
        font.setPointSize(50 * self.gui.font_scale_ratio)

        self.board_objects = []  # An empty array to start
        self.abort_button_enabled = False
        
        # Sidebar Abort Button Config
        self.abort_button = QPushButton()
        self.abort_button.setDefault(False)
        self.abort_button.setAutoDefault(False)
        self.abort_button.setFont(font)
        self.abort_button.setFixedWidth(self.width - 15)
        self.abort_button.clicked.connect(self.abort_init)
        self.abort_button.setDisabled(True)

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
        self.scroll.move(2, (150 * self.gui.pixel_scale_ratio[1]) + self.tabWidget.height() + 10)
        self.scroll.setFixedHeight(700 * self.gui.pixel_scale_ratio[1])
        self.scroll.show()

        self.buttonLayout.addWidget(self.abort_button)
        self.buttonLayout.setAlignment(self.abort_button, Qt.AlignBottom | Qt.AlignCenter)

        self.buffer_label = QLabel(self)
        self.buffer_label.setFont(title_font)
        self.buffer_label.setStyleSheet("color: white")
        self.buffer_label.setText("  ")
        self.buffer_label.setFixedHeight(75 * self.gui.pixel_scale_ratio[1])
        self.buffer_label.setFixedWidth(5*self.width)
        self.buffer_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.buffer_label.move(10 * self.gui.pixel_scale_ratio[0], 0)  # Nasty but makes it look more centered
        self.buttonLayout.addWidget(self.buffer_label)

        self.buffer_label2 = QLabel(self)
        self.buffer_label2.setFont(title_font)
        self.buffer_label2.setStyleSheet("color: white")
        self.buffer_label2.setText("  ")
        self.buffer_label2.setFixedHeight(75 * self.gui.pixel_scale_ratio[1])
        self.buffer_label2.setFixedWidth(5*self.width)
        self.buffer_label2.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.buffer_label2.move(10 * self.gui.pixel_scale_ratio[0], 0)  # Nasty but makes it look more centered
        #self.buttonLayout.addWidget(self.buffer_label2)

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

    @overrides
    def update(self):
        super().update()
        # self.last_packet = self.window.last_packet
        # if self.last_packet:
        #     for board in self.board_objects:
        #         board_name = board.name
        #         prefix = self.interface.getPrefix(board_name)
        #
        #         if board_name == "Flight Computer":
        #             board.update(self.last_packet[prefix+"e_batt"], 0, self.last_packet[prefix+"STATE"], False, self.last_packet[prefix+"timestamp"], self.last_packet[prefix+"adc_rate"], self.last_packet[prefix+"telem_rate"]) # no flash state yet, no i_batt
        #         elif board_name == "Black Box":
        #             board.update(0, 0, self.last_packet[prefix+"STATE"], False, self.last_packet[prefix+"timestamp"], self.last_packet[prefix+"adc_rate"], self.last_packet[prefix+"telem_rate"]) # no flash state yet, no i_batt, no e_batt
        #         elif board_name == "Pressurization Controller":
        #             board.update(self.last_packet[prefix + "e_batt"], self.last_packet[prefix + "i_batt"],
        #                          self.last_packet[prefix + "STATE"], self.last_packet[prefix + "LOGGING_ACTIVE"], self.last_packet[prefix + "timestamp"],
        #                          self.last_packet[prefix + "adc_rate"], self.last_packet[prefix + "telem_rate"],
        #                          self.last_packet[prefix + "state_rem_duration"])
        #         elif board_name == "GSE Controller":
        #             board.update(self.last_packet[prefix + "e_batt"], self.last_packet[prefix + "ibus"],
        #                          self.last_packet[prefix + "STATE"], self.last_packet[prefix + "LOGGING_ACTIVE"], self.last_packet[prefix + "timestamp"],
        #                          self.last_packet[prefix + "adc_rate"], self.last_packet[prefix + "telem_rate"],
        #                          0)  # no flash state yet
        #         else:
        #             board.update(self.last_packet[prefix+"e_batt"], self.last_packet[prefix+"i_batt"], self.last_packet[prefix+"STATE"], False, self.last_packet[prefix+"timestamp"], self.last_packet[prefix+"adc_rate"], self.last_packet[prefix+"telem_rate"], 0) # no flash state yet


        # TODO: see https://gitlab.eecs.umich.edu/masa/avionics/gui/-/issues/41
        # checks whether the Software Abort Button is enabled or not
        if self.abort_button_enabled:
            # if the button is enabled from the "Abort Button" settings menu
            self.abort_button.setText("Abort")
            self.abort_button.setStyleSheet("background-color : darkred")
            self.abort_button.setDisabled(False)
        else: # button is disabled (well, it just doesn't do anything)
            self.abort_button.setText("Disabled")
            self.abort_button.setStyleSheet("color : gray")
            self.abort_button.setDisabled(True)


class SidebarTabWidget(QWidget):

    def __init__(self, parent):

        super().__init__(parent)

        self.controlsSidebarWidget = parent
        self.gui = self.controlsSidebarWidget.gui

        self.setFixedHeight(int(300 * self.gui.pixel_scale_ratio[1]))
        self.setFixedWidth(self.controlsSidebarWidget.width)

        self.tabWidget = QTabWidget(self)
        self.tabWidget.setFixedWidth(self.width())
        self.tabWidget.setFixedHeight(self.height())

        self.noteWidget = SidebarNoteWidget(self.tabWidget, self.controlsSidebarWidget)

        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.tab2.setStyleSheet("background-color:red;")

        self.tabWidget.addTab(self.noteWidget, "Notes")
        self.tabWidget.addTab(self.tab2, "Test2")

        self.setStyleSheet("background-color:blue;")

        self.show()


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
        self.noteBox.setColumnWidth(1, math.floor(self.parent.width() * .65)-35)
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

        self.noteBox.setAutoFillBackground(True)
        p = self.noteBox.palette()
        p.setColor(self.noteBox.backgroundRole(), Constants.MASA_Blue_color)
        self.noteBox.setPalette(p)

        self.noteBox.setFrameShape(QFrame.NoFrame)

        self.noteBox.show()

        self.lineEdit = QLineEdit(self)
        self.lineEdit.returnPressed.connect(self.enterNewNote)
        self.lineEdit.setPlaceholderText("Start campaign for notes")
        self.lineEdit.setDisabled(True)
        self.lineEdit.show()
        self.lineEdit.clearFocus()

        self.vlayout.addWidget(self.lineEdit)

        self.setStyleSheet("background-color:red;")

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
        item.setBackground(Constants.MASA_Blue_color)
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
