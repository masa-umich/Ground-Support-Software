from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import Constants
from board import Board

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
        self.noteBoxText = "Write notes here"

        # Create the label that will hold the status label, displays what task is being performed
        title_font = QFont()
        title_font.setStyleStrategy(QFont.PreferAntialias)
        title_font.setFamily(Constants.monospace_font)
        title_font.setPointSizeF(48 * self.gui.font_scale_ratio)
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
        self.state_time_label.setText("Rem Time: 00 qs")
        self.state_time_label.setFixedHeight(75 * self.gui.pixel_scale_ratio[1])
        self.state_time_label.setFixedWidth(self.width)
        self.state_time_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.state_time_label.move(10 * self.gui.pixel_scale_ratio[0], 85 * self.gui.pixel_scale_ratio[1])  # Nasty but makes it look more centered
        self.state_time_label.show()

        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setFamily(Constants.default_font)
        font.setPointSize(12 * self.gui.font_scale_ratio)

        self.noteBox = QTextEdit(self)
        self.noteBox.setFont(font)
        self.noteBox.setFixedWidth(self.width)
        self.noteBox.setFixedHeight(self.width - 85 * self.gui.pixel_scale_ratio[1])
        self.noteBox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.noteBox.move(0, 160 * self.gui.pixel_scale_ratio[1])
        self.noteBox.setText(self.noteBoxText)
        self.noteBox.show()

        self.state_frame = QFrame(self)
        self.state_frame.setGeometry(self.left, 0, self.width*3,
                                     80 * self.gui.pixel_scale_ratio[1])
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
        self.abort_button.setFixedWidth(self.width - 100)
        self.abort_button.clicked.connect(self.abort_init)
        self.abort_button.setDisabled(False)

        self.buttonLayout.addStretch()
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
        self.buttonLayout.addWidget(self.buffer_label2)


    def addBoards(self, boardNames: []):
        """
        Add in boards to be shown on the sidebar. Only need to pass in the name
        :param boardNames: A list of board names that needs to be passed
        """
        y_pos = (88 * self.gui.pixel_scale_ratio[1] + 1) + self.width

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

        self.window.statusBar().showMessage("Boards: " + str(boardNames) + " added")

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
            save_dict["Board"+str(i)] = board.name

        return save_dict

    @overrides
    def update(self):
        super().update()
        self.last_packet = self.window.last_packet
        if self.last_packet:
            for board in self.board_objects:
                board_name = board.name
                prefix = self.interface.getPrefix(board_name)
                
                if board_name == "Flight Computer":
                    board.update(self.last_packet[prefix+"e_batt"], 0, self.last_packet[prefix+"STATE"], False, self.last_packet[prefix+"timestamp"], self.last_packet[prefix+"adc_rate"], self.last_packet[prefix+"telem_rate"]) # no flash state yet, no i_batt
                elif board_name == "Black Box":
                    board.update(0, 0, self.last_packet[prefix+"STATE"], False, self.last_packet[prefix+"timestamp"], self.last_packet[prefix+"adc_rate"], self.last_packet[prefix+"telem_rate"]) # no flash state yet, no i_batt, no e_batt
                elif board_name == "Pressurization Controller":
                    board.update(self.last_packet[prefix + "e_batt"], self.last_packet[prefix + "i_batt"],
                                 self.last_packet[prefix + "STATE"], self.last_packet[prefix + "LOGGING_ACTIVE"], self.last_packet[prefix + "timestamp"],
                                 self.last_packet[prefix + "adc_rate"], self.last_packet[prefix + "telem_rate"],
                                 self.last_packet[prefix + "state_rem_duration"])
                elif board_name == "GSE Controller":
                    board.update(self.last_packet[prefix + "e_batt"], self.last_packet[prefix + "ibus"],
                                 self.last_packet[prefix + "STATE"], self.last_packet[prefix + "LOGGING_ACTIVE"], self.last_packet[prefix + "timestamp"],
                                 self.last_packet[prefix + "adc_rate"], self.last_packet[prefix + "telem_rate"],
                                 0)  # no flash state yet
                else:
                    board.update(self.last_packet[prefix+"e_batt"], self.last_packet[prefix+"i_batt"], self.last_packet[prefix+"STATE"], False, self.last_packet[prefix+"timestamp"], self.last_packet[prefix+"adc_rate"], self.last_packet[prefix+"telem_rate"], 0) # no flash state yet

        if self.abort_button_enabled:
            # if the button is enabled from the "Abort Button" settings menu
            self.abort_button.setText("Abort")
            self.abort_button.setStyleSheet("background-color : darkred")
        else: # button is disabled (well, it just doesn't do anything)
            self.abort_button.setText("Disabled")
            self.abort_button.setStyleSheet("color : gray")