import json
import time
import math
import atexit
from threading import Thread
import interface


PROGRAMS = {}


class InterfaceThread(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.parent = parent
        self.dmx = interface.Interface()
        self.start_time = time.time()
        self.is_running = True
        atexit.register(self.stop)

    def run(self):
        while self.is_running:
            elapsed = time.time() - self.start_time
            universe = self.parent.compute_at(elapsed)

            self.dmx.stream(universe)

            time.sleep(1 / float(interface.FRAMERATE))

        self.dmx.close()
        print "Interface Thread Stopped"

    def stop(self):
        self.is_running = False


class Streamer(object):

    def __init__(self, programs_file=None):
        self.load(programs_file)
        self.universe_expressions = ["0"] * 512
        self.selected_program_id = -1
        self.selected_program_name = ""

        self.interface_thread = InterfaceThread(parent=self)
        self.interface_thread.start()

    def load(self, programs_file):
        if programs_file is not None:
            with open(programs_file, 'r') as f_programs:
                self.programs = json.load(f_programs)
        else:
            self.programs = PROGRAMS
        self.program_names = sorted(self.programs.keys())

    def program_clicked(self, program_name):
        self.selected_program_id = self.program_names.index(program_name)
        self.selected_program_name = program_name

    def compute_at(self, elapsed):
        if self.selected_program_id != -1:
            program = self.programs[self.selected_program_name]

            for channel_expression, value_expression in program.items():
                channels = eval(channel_expression)
                try:
                    for channel in iter(channels):
                        self.universe_expressions[channel] = value_expression
                except TypeError:
                    self.universe_expressions[channels] = value_expression

        universe = bytearray([0] * 512)

        for channel, expression in enumerate(self.universe_expressions):
            universe[channel] = int(255 * min(1.0, max(0.0, eval(expression))))

        return universe

    def ui_status(self):
        return {
            'selected_program': self.selected_program_name
        }

    def stop(self):
        self.interface_thread.stop()
