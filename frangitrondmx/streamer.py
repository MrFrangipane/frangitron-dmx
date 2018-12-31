import json
import time
import math
import random
import atexit
from os import path, listdir
from threading import Thread
import interface
from fixtures import Fixture

_elapsed = 0.0
_channel = 0
cos2 = lambda x: math.cos(x) * 0.5 + 0.5
sin2 = lambda x: math.sin(x) * 0.5 + 0.5


class State(object):
    def __init__(self, context, exception=None):
        self.context = context
        self.exception = exception

    def __nonzero__(self):
        return self.exception is None


def lerp(start, end, factor):
    return factor * end + (1.0 - factor) * start


def elapsed(step=0):
    global _elapsed
    if step == 0: return _elapsed
    return (_elapsed // step) * step


def _seed(step, per_channel, function_, *args, **kwargs):
    if per_channel:
        global _channel
        random.seed(elapsed(step) + _channel)
    else:
        random.seed(elapsed(step))

    return function_(*args, **kwargs)


def choice(iter_, step=0, per_channel=True):
    return _seed(step, per_channel, random.choice, iter_)


def randint(min_, max_, step=0, per_channel=True):
    return _seed(step, per_channel, random.randint, min_, max_)


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
        self.state = State(context="Initialized")
        self.load(programs_file=programs_file)
        self._load_fixtures(fixtures_folder)
        self.universe_expressions = ["0"] * 512
        self.selected_program_id = -1
        self.selected_program_name = ""

        self.interface_thread = InterfaceThread(parent=self)
        self.interface_thread.start()

    def reset_expressions(self):
        self.universe_expressions = ["0"] * 512

    def reset_state(self):
        self.state = State(context="Reset")

    def _load_fixtures(self, fixtures_folder):
        self.fixtures = dict()

        folders = [
            path.join(fixtures_folder, folder) for folder
            in listdir(fixtures_folder) if path.isdir(path.join(fixtures_folder, folder))
        ]
        for folder in folders:
            try:
                new_fixture = Fixture.from_folder(folder)
                self.fixtures[new_fixture.name] = new_fixture
            except KeyError as e:
                pass

    def load(self, programs_file=None, programs_source=None):
        if not self.state: return
        if programs_file is not None:
            try:
                with open(programs_file, 'r') as f_programs:
                    self.programs = json.load(f_programs)
                self.state = State(context="Programs loaded")
            except ValueError, e:
                self.state = State(context="Loading programs from file", exception=e)
                self.programs = dict()

        elif programs_source is not None:
            try:
                self.programs = json.loads(programs_source)
                self.state = State(context="Programs loaded")
            except ValueError, e:
                self.state = State(context="Loading programs from source", exception=e)
                self.programs = dict()

        else:
            self.programs = dict()
            self.state = State(context="No programs")

        self.program_names = sorted(self.programs.keys())

    def program_clicked(self, program_name):
        if not self.state: return

        try:
            self.selected_program_id = self.program_names.index(program_name)
            self.selected_program_name = program_name
            self.state = State(context="Program changed")

        except ValueError as e:
            self.state = State(context="Changing program", exception=e)
            self.selected_program_id = -1
            self.selected_program_name = ""

    def compute(self):
        global _channel
        if not self.state:
            return bytearray([0] * 513)

        if self.selected_program_id != -1:
            program = self.programs[self.selected_program_name]

            for data in program:
                fixture = self.fixtures[data['fixture']]
                fixture.address = data['address']

                for program_name in data['programs']:
                    program = fixture.programs.get(program_name, None)
                    if program is None: continue

                    for channel_name, channel_expression in  program.expressions.items():
                        try:
                            channel_address = fixture.channel_address(channel_name)
                        except Exception as e:
                            self.state = State(context="Channel addressing", exception=e)
                            return bytearray([0] * 513)

                        self.universe_expressions[channel_address] = channel_expression

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
                self.state = State(
                    context="Computing value '{}'".format(expression),
                    exception=e
                )
                return bytearray([0] * 513)
        print list(universe[0:30])
        self.state = State(context="Computed")
        return universe

    def ui_status(self):
        return {
            'selected_program': self.selected_program_name
        }

    def stop(self):
        self.interface_thread.stop()
