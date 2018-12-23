import time
import math
from threading import Thread
import interface


class InterfaceThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.dmx = interface.Interface()
        self.universe = bytearray([0] * 512)
        self.start_time = time.time()

    def run(self):
        while True:
            elapsed = time.time() - self.start_time

            self.universe[1] = int(255 * (0.5 * math.cos(elapsed * math.pi * 0.25) + 0.5))
            self.universe[2] = int(255 * (0.5 * math.cos(elapsed * math.pi * 0.25 + math.pi) + 0.5))

            self.dmx.stream(self.universe)
            time.sleep(1 / float(interface.FRAMERATE))


class Streamer(object):

    def __init__(self):
        self.programs = list()
        self.selected_program = -1
        self.interface_thread = InterfaceThread()
        self.interface_thread.start()

    def load(self):
        self.programs = ['Blackout', 'ChitChat', 'Lounge', 'Club', 'Searchlight', 'Apocalypse']

    def program_clicked(self, program_name):
        self.selected_program = self.programs.index(program_name)

    def ui_status(self):
        return {
            'selected_program': self.programs[self.selected_program]
        }
