from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys


class Slider(QSlider):
    minimumChanged = pyqtSignal(int)
    maximumChanged = pyqtSignal(int)

    def setMinimum(self, minimum):
        self.minimumChanged.emit(minimum)
        super(Slider, self).setMinimum(minimum)

    def setMaximum(self, maximum):
        self.maximumChanged.emit(maximum)
        super(Slider, self).setMaximum(maximum)


class ConfirmBox(QDialog):
    def __init__(self, sureness=8, minVal=0, maxVal=10):
        super().__init__()

        self.sureness = sureness

        self.setWindowTitle("Really?")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        caption = QLabel("How sure are you?")
        self.slider = Slider(tickPosition=QSlider.TicksBelow, orientation=Qt.Horizontal)
        slider_vbox = QVBoxLayout()
        slider_hbox = QHBoxLayout()
        slider_hbox.setContentsMargins(0, 0, 0, 0)
        slider_vbox.setContentsMargins(0, 0, 0, 0)
        slider_vbox.setSpacing(0)
        label_minimum = QLabel(alignment=Qt.AlignLeft)
        self.slider.minimumChanged.connect(label_minimum.setNum)
        label_maximum = QLabel(alignment=Qt.AlignRight)
        self.slider.maximumChanged.connect(label_maximum.setNum)
        slider_vbox.addWidget(self.slider)
        slider_vbox.addLayout(slider_hbox)
        slider_hbox.addWidget(label_minimum, Qt.AlignLeft)
        slider_hbox.addWidget(label_maximum, Qt.AlignRight)
        slider_vbox.addStretch()

        self.slider.setMinimum(minVal)
        self.slider.setMaximum(maxVal)
        self.slider.setValue(minVal)

        self.layout.addWidget(caption)
        self.layout.addLayout(slider_vbox)
        self.slider.valueChanged.connect(self._update)

        self.continueButton = QPushButton("Continue")
        self.cancelButton = QPushButton("Cancel")
        button_hbox = QHBoxLayout()
        button_hbox.addWidget(self.continueButton)
        button_hbox.addWidget(self.cancelButton)
        self.layout.addLayout(button_hbox)

        self.continueButton.setEnabled(False)

    def show(self):
        ret = QMessageBox.question(
            self,
            "Confirm",
            "Are you sure?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ret == QMessageBox.Yes:
            super().show()
            self.setGeometry(300, 300, 300, 150)

    def _update(self, value):
        self.continueButton.setEnabled(value >= self.sureness)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    b = ConfirmBox(9, 0, 10)
    b.show()
    sys.exit(app.exec_())
