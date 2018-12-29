import json
import time
import math
import random
import atexit
from threading import Thread
import interface
from fixtures import Fixture


_elapsed = 0.0
_channel = 0
cos2 = lambda x: math.cos(x) * 0.5 + 0.5
sin2 = lambda x: math.sin(x) * 0.5 + 0.5


def lerp(start, end, factor):
    return factor * end + (1.0 - factor) * start


def elapsed(step=0):
    global _elapsed
    if step == 0: return _elapsed
    return (_elapsed // step) * step


def _seed(step, function_, *args, **kwargs):
    global _channel
    random.seed(elapsed(step) + _channel)
    return function_(*args, **kwargs)


def choice(iter_, step=0):
    return _seed(step, random.choice, iter_)


def randint(min_, max_, step=0):
    return _seed(step, random.randint, min_, max_)


class InterfaceThread(Thread):

    def __init__(self, parent):
        Thread.__init__(self)
        self.parent = parent
        self.dmx = interface.Interface()
        self.start_time = time.time()
        self.is_running = True
        atexit.register(self.stop)

    def run(self):
        global _elapsed
        while self.is_running:
            _elapsed = time.time() - self.start_time
            universe = self.parent.compute()
            self.dmx.stream(universe)

            time.sleep(1 / float(interface.FRAMERATE))

        self.dmx.close()
        print "Interface Thread Stopped"

    def stop(self):
        self.is_running = False


class Streamer(object):

    def __init__(self, fixtures_folder, programs_file=None):
        self.load(programs_file=programs_file)
        self._load_fixtures(fixtures_folder)
        self.universe_expressions = ["0"] * 512
        self.selected_program_id = -1
        self.selected_program_name = ""
        self.error_state = None

        self.interface_thread = InterfaceThread(parent=self)
        self.interface_thread.start()

    def _load_fixtures(self, fixtures_folder):
        with open("E:/PROJETS/dev/frangitron-dmx/frangitrondmx/fixtures/cameo-wookie-600b.json", "r") as f_fixture:
            data = json.load(f_fixture)
        self.fixtures = [Fixture.from_dict(data)]

    def load(self, programs_file=None, programs_source=None):
        if programs_file is not None:
            try:
                with open(programs_file, 'r') as f_programs:
                    self.programs = json.load(f_programs)
            except ValueError, e:
                self.error_state = e
                self.programs = dict()

        elif programs_source is not None:
            try:
                self.programs = json.loads(programs_source)
            except ValueError, e:
                self.error_state = e
                self.programs = dict()

        else:
            self.programs = dict()

        self.program_names = sorted(self.programs.keys())

    def program_clicked(self, program_name):
        try:
            self.selected_program_id = self.program_names.index(program_name)
            self.selected_program_name = program_name
        except ValueError as e:
            self.error_state = e
            self.selected_program_id = -1
            self.selected_program_name = ""

    def compute(self):
        global _channel
        self.error_state = None

        if self.selected_program_id != -1:
            program = self.programs[self.selected_program_name]

            for channel_expression, value_expression in program.items():
                try:
                    channels = eval(channel_expression)
                except Exception as e:
                    self.error_state = e
                    continue

                try:
                    for channel in iter(channels):
                        self.universe_expressions[channel] = value_expression
                except Exception as e:
                    try:
                        self.universe_expressions[channels] = value_expression
                    except Exception as e:
                        self.error_state = e

        universe = bytearray([0] * 513)

        for channel, expression in enumerate(self.universe_expressions):
            try:
                if expression[0] == '$':
                    expression = expression[1:]
                    factor = 1
                else:
                    factor = 255

                _channel = channel
                universe[channel] = min(255, max(0, int(factor * eval(expression))))
            except Exception as e:
                self.error_state = e

        if self.error_state is None:
            return universe
        else:
            return bytearray([0] * 513)

    def ui_status(self):
        return {
            'selected_program': self.selected_program_name
        }

    def stop(self):
        self.interface_thread.stop()
