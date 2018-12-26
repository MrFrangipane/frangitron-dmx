import time
import math
from threading import Thread
import interface


PROGRAMS = {
    'Blackout': {},
    'Greenow' : {
        1: "0.5 * math.cos(elapsed * math.pi * 0.25) + 0.5",
        2: "0.5 * math.cos(elapsed * math.pi * 0.25 + math.pi) + 0.5",
        3: "1.0 if elapsed % 1 > 0.5 else 0.0"
    },
    'Strobe': {
        1: "1.0 if elapsed % .1 > 0.05 else 0.0",
        2: "1.0 if elapsed % .1 > 0.05 else 0.0",
        3: "1.0 if elapsed % .1 > 0.05 else 0.0"
    }
}


class InterfaceThread(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.parent = parent
        self.dmx = interface.Interface()
        self.start_time = time.time()

    def run(self):
        while True:
            elapsed = time.time() - self.start_time
            universe = self.parent.compute_at(elapsed)[:]
            self.dmx.stream(universe)
            time.sleep(1 / float(interface.FRAMERATE))


class Streamer(object):

    def __init__(self):
        self.programs = list()
        self.universe = bytearray([0] * 512)
        self.selected_program_id = -1
        self.selected_program_name = ""

        self.load()

        self.interface_thread = InterfaceThread(parent=self)
        self.interface_thread.start()

    def load(self):
        self.programs = sorted(PROGRAMS.keys())

    def program_clicked(self, program_name):
        self.selected_program_id = self.programs.index(program_name)
        self.selected_program_name = program_name

    def compute_at(self, elapsed):
        self.universe = bytearray([0] * 512)
        if self.selected_program_id == -1: return self.universe

        program = PROGRAMS[self.selected_program_name]
        for channel, expression in program.items():
            value = int(255 * min(1.0, max(0.0, eval(expression))))
            self.universe[channel] = value

        return self.universe

    def ui_status(self):
        return {
            'selected_program': self.selected_program_name
        }
