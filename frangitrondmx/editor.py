from time import sleep
from PySide.QtGui import QApplication, QWidget, QGridLayout, QLabel, QPlainTextEdit, QFont, QComboBox, QSpinBox
from PySide.QtCore import QTimer
from streamer import Streamer


TEMPLATE = """{
  "1": {
    "1": "1.0",
    "2": "1.0",
    "3": "1.0"
  }
}"""
BLACKOUT = '{ "1": {"range(1, 512)": "0"}}'
FRAMERATE = 5


class MainWindow(QWidget):
    def __init__(self, fixtures_folder, filename, parent=None):
        QWidget.__init__(self, parent)

        self.filename = filename
        with open(self.filename, 'r') as f_program:
            text = f_program.read()

        self.setWindowTitle("Frangitron DMX program editor")

        self.text = QPlainTextEdit()
        font = QFont("Monospace")
        font.setStyleHint(QFont.TypeWriter)
        font.setPixelSize(16)
        self.text.setFont(font)
        self.text.setStyleSheet("color: white; background-color: rgb(30, 30, 30)")
        self.text.setPlainText(text)

        self.combo_fixture = QComboBox()
        self.spinner_offset = QSpinBox()
        self.spinner_offset.setMinimum(1)
        self.spinner_offset.setMaximum(512)
        self.spinner_offset.setValue(1)
        self.spinner_offset.valueChanged.connect(self.fixture_changed)

        self.doc = QPlainTextEdit()
        self.doc.setReadOnly(True)
        self.doc.setFont(font)

        self.status = QLabel()

        layout = QGridLayout(self)
        layout.addWidget(self.combo_fixture, 0, 1)
        layout.addWidget(self.spinner_offset, 0, 2)
        layout.addWidget(self.text, 0, 0, 2, 1)
        layout.addWidget(self.doc, 1, 1, 1, 2)
        layout.addWidget(self.status, 2, 0, 1, 3)
        layout.setColumnStretch(0, 60)
        layout.setColumnStretch(1, 40)

        self.resize(1280, 800)

        self.streamer = Streamer(fixtures_folder)

        self.combo_fixture.addItems([fixture.name for fixture in self.streamer.fixtures])
        self.combo_fixture.currentIndexChanged.connect(self.fixture_changed)

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(500.0 / FRAMERATE)
        self.should_reload = True

        self.fixture_changed()

    def fixture_changed(self):
        self.current_fixture = self.streamer.fixtures[self.combo_fixture.currentIndex()]
        self.current_fixture.address = self.spinner_offset.value()
        self.doc.setPlainText(self.current_fixture.doc())

    def tick(self):
        if self.should_reload:
            self.streamer.reset_state()
            self.streamer.load(programs_source=self.text.toPlainText())
            self.streamer.program_clicked("1")

        else:
            state = self.streamer.state

            if state:
                self.status.setStyleSheet("background-color: green; color: white; padding: 5px")
                self.status.setText(state.context)
            else:
                self.status.setStyleSheet("background-color: red; color: white; padding: 5px")
                self.status.setText("{} : {}".format(state.context, state.exception))

            if self.filename is None: return

            with open(self.filename, 'w') as f_programs:
                f_programs.write(self.text.toPlainText())

        self.should_reload = not self.should_reload

    def closeEvent(self, event):
        self.timer.stop()
        self.streamer.load(programs_source=BLACKOUT)
        self.streamer.program_clicked("1")
        sleep(2.0 / float(FRAMERATE))
        self.streamer.stop()
        event.accept()


def launch_editor(fixtures_folder, filename):
    app = QApplication([])

    main_window = MainWindow(fixtures_folder, filename)
    main_window.show()

    app.exec_()


if __name__ == '__main__':
    launch_editor()
