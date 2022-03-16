from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
from overrides import overrides


class PartyParrot(QLabel):
    def __init__(self):
        super().__init__()
        self.current_frame = 0
        
        self.frames = []
        for i in range(10):
            self.frames.append(QPixmap("Images/Parrot/frame{}.png".format(i)))
        
        self.setAlignment(Qt.AlignCenter)
        self._set_frame()
        

    def _set_frame(self):
        self.setPixmap(self.frames[self.current_frame])

    def step(self):
        self.current_frame = (self.current_frame + 1) % 10
        self._set_frame()
    
    @overrides
    def setFixedSize(self, h, w, *args, **kwargs):
        super().setFixedSize(h, w, *args, **kwargs)
        for i in range(10):
            frame = QPixmap("Images/Parrot/frame{}.png".format(i))
            self.frames[i] = frame.scaled(h, w, Qt.KeepAspectRatio)

if __name__ == "__main__":
    #QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    # init window
    cycle_time = 20 # in ms
    pp = PartyParrot()
    #pp.setFixedSize(50, 50)

    #timer and tick updates
    timer = QTimer()
    timer.timeout.connect(pp.step)
    timer.start(cycle_time)

    # run
    pp.show()
    sys.exit(app.exec())