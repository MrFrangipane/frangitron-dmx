from time import sleep
from PySide.QtGui import QApplication, QWidget, QGridLayout, QLabel, QPlainTextEdit, QFont, QComboBox, QSpinBox
from PySide.QtCore import QTimer
from streamer import Streamer

PROGRAM = '''{
  "1": [
    {
      "fixture": "__fixture__", 
      "address": __address__, 
      "programs": ["__program__"]
    }
  ]
}'''
FRAMERATE = 5


class MainWindow(QWidget):
    def __init__(self, fixtures_folder, parent=None):
        QWidget.__init__(self, parent)
        self.current_fixture = None
        self.fixtures_folder = fixtures_folder
        self.setWindowTitle("Frangitron DMX program editor")

        self.text = QPlainTextEdit()
        font = QFont("Monospace")
        font.setStyleHint(QFont.TypeWriter)
        font.setPixelSize(16)
        self.text.setFont(font)
        self.text.setStyleSheet("color: white; background-color: rgb(30, 30, 30)")

        self.combo_fixture = QComboBox()

        self.combo_programs = QComboBox()

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
        layout.addWidget(self.combo_programs, 1, 1)
        layout.addWidget(self.text, 0, 0, 3, 1)
        layout.addWidget(self.doc, 2, 1, 1, 2)
        layout.addWidget(self.status, 3, 0, 1, 3)
        layout.setColumnStretch(0, 60)
        layout.setColumnStretch(1, 40)

        self.resize(1280, 800)

        self.streamer = Streamer(self.fixtures_folder)

        self.combo_fixture.addItems(sorted(self.streamer.fixtures))
        self.combo_fixture.currentIndexChanged.connect(self.fixture_changed)

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(500.0 / FRAMERATE)
        self.should_reload = True

        self.fixture_changed()

    def update_programs(self):
        self.combo_programs.blockSignals(True)
        selected_program = self.combo_programs.currentText()

        new_programs = sorted(self.current_fixture.programs.keys())
        self.combo_programs.clear()
        self.combo_programs.addItems(new_programs)

        if selected_program in new_programs:
            self.combo_programs.setCurrentIndex(self.combo_programs.findText(selected_program))

        self.combo_programs.blockSignals(False)

    def fixture_changed(self):
        self.current_fixture = self.streamer.fixtures[self.combo_fixture.currentText()]
        self.current_fixture.address = self.spinner_offset.value()
        self.update_programs()
        self.doc.setPlainText(self.current_fixture.doc())
        with open(self.current_fixture.programs_filepath, 'r') as f_programs:
            self.text.setPlainText(f_programs.read())

    def tick(self):
        if self.should_reload:
            self.current_fixture.reload_programs()
            self.update_programs()
            self.streamer.reset_state()
            program = PROGRAM.replace('__fixture__', self.current_fixture.name)
            program = program.replace('__address__', str(self.current_fixture.address))
            program = program.replace('__program__', self.combo_programs.currentText())
            self.streamer.load(programs_source=program)
            self.streamer.program_clicked("1")

        else:
            state = self.streamer.state

            if state:
                self.status.setStyleSheet("background-color: green; color: white; padding: 5px")
                self.status.setText(state.context)
            else:
                self.status.setStyleSheet("background-color: red; color: white; padding: 5px")
                self.status.setText("{} : {}".format(state.context, state.exception))

            if self.current_fixture is None: return

            with open(self.current_fixture.programs_filepath, 'w') as f_programs:
                f_programs.write(self.text.toPlainText())

        self.should_reload = not self.should_reload

    def closeEvent(self, event):
        self.timer.stop()
        self.streamer.load(programs_source="")
        self.streamer.program_clicked("1")
        sleep(2.0 / float(FRAMERATE))
        self.streamer.stop()
        event.accept()


def launch_editor(fixtures_folder):
    app = QApplication([])

    main_window = MainWindow(fixtures_folder)
    main_window.show()

    app.exec_()


if __name__ == '__main__':
    launch_editor()
