from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import cv2


"""
This file contains the class to create a window for showing live video
"""

class LiveVideoWindow(QMainWindow):
    """
    Window to house the video feeds
    """

    def __init__(self, parent = None):
        super().__init__()
        self.title = 'PyQt5 Video'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        self.camera_index = 0
        self.video_button = QPushButton(self)
        self.camera_thread = Thread(self)

        self.initUI()
        self.show()

    @pyqtSlot(QImage)
    def setImage(self, image):
        """
        Sets the image on the button to be displayed
        """
        self.video_button.setIcon(QIcon(QPixmap.fromImage(image)))
        self.video_button.setIconSize(image.size())
        self.video_button.resize((image.size()))

    def initUI(self):
        """
        Basic init for UI elements
        """
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(1800, 1200)

        self.video_button.move(280, 120)
        self.video_button.resize(640, 480)
        self.video_button.setIconSize(QSize(640,480))
        self.video_button.clicked.connect(lambda: self.toggleCamera())

        self.camera_thread.changePixmap.connect(self.setImage)
        self.camera_thread.start()

    def toggleCamera(self):
        """
        Switches between camera when the user loads cameras
        """
        if self.camera_index == 0:
            self.camera_index = 1
        else:
            self.camera_index = 0

        self.camera_thread.changeFeed(self.camera_index)





class Thread(QThread):
    """
    Thread class to get live video input
    """

    changePixmap = pyqtSignal(QImage)

    def __init__(self, parent=None):
        self.currentFeed = None
        self.currentIndex = 0

        super().__init__()

    def run(self):
        """
        Called when thread is started
        """
        self.currentFeed = cv2.VideoCapture(self.currentIndex)
        while True:
            ret, frame = self.currentFeed.read()
            if ret:
                # https://stackoverflow.com/a/55468544/6622587
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

    def changeFeed(self, index):
        """
        Called to change which feed is displated
        """
        self.currentIndex = index
        self.currentFeed = cv2.VideoCapture(self.currentIndex)

