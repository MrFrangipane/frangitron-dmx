from PySide.QtGui import QApplication, QWidget, QVBoxLayout, QLabel, QPlainTextEdit, QFont
from PySide.QtCore import QTimer
from streamer import Streamer


TEMPLATE = """{
  "1": {
    "1": "1.0",
    "2": "1.0",
    "3": "1.0"
  }
}"""
FRAMERATE = 30


class MainWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.setWindowTitle("Frangitron DMX program editor")

        self.text = QPlainTextEdit()
        font = QFont("Monospace")
        font.setStyleHint(QFont.TypeWriter)
        font.setPixelSize(16)
        self.text.setFont(font)
        self.text.setStyleSheet("color: white; background-color: rgb(30, 30, 30)")
        self.text.setPlainText(TEMPLATE)

        self.status = QLabel()

        layout = QVBoxLayout(self)
        layout.addWidget(self.text)
        layout.addWidget(self.status)

        self.resize(800, 600)

        self.streamer = Streamer()

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000 / FRAMERATE)

    def tick(self):
        self.streamer.load(programs_source=self.text.toPlainText())
        self.streamer.program_clicked("1")

        if self.streamer.error_state is None:
            self.status.setStyleSheet("background-color: green; color: white; padding: 5px")
            self.status.setText("Streaming...")
        else:
            self.status.setStyleSheet("background-color: red; color: white; padding: 5px")
            self.status.setText(str(self.streamer.error_state))


def launch_editor():
    app = QApplication([])

    main_window = MainWindow()
    main_window.show()

    app.exec_()


if __name__ == '__main__':
    launch_editor()
