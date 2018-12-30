"""
Inspired by
Copyright (C) Jonathan Brogdon <jlbrogdon@gmail.com>
His program is published under a GPLv2 license
"""
import time
import math
from usb import USBError
from pyftdi.ftdi import Ftdi


VENDOR = 0x0403
PRODUCT = 0x6001
FRAMERATE = 100


class Interface(object):
    def __init__(self):
        self.baud_rate = 250000
        self.data_bits = 8
        self.stop_bits = 2
        self.parity = 'N'
        self.flow_ctrl = ''
        self.rts_state = 0
        self._is_open = False
        self._init_dmx()

    def _init_dmx(self):
        self.ftdi = Ftdi()
        try:
            self.ftdi.open(VENDOR, PRODUCT, 0)
            self.ftdi.set_baudrate(self.baud_rate)
            self.ftdi.set_line_property(self.data_bits, self.stop_bits, self.parity, break_=Ftdi.BREAK_OFF)
            self.ftdi.set_flowctrl(self.flow_ctrl)
            self.ftdi.purge_buffers()
            self.ftdi.set_rts(self.rts_state)
            self._is_open = True
        except USBError, e:
            print e
            self._is_open = False

    def stream(self, universe_byte_array):
        if not self._is_open: return

        self.ftdi.write_data(universe_byte_array)
        self.ftdi.set_line_property(self.data_bits, self.stop_bits, self.parity, break_=Ftdi.BREAK_ON)
        self.ftdi.set_line_property(self.data_bits, self.stop_bits, self.parity, break_=Ftdi.BREAK_ON)

        self.ftdi.close()
        self._init_dmx()

    def close(self):
        if not self._is_open: return
        self._is_open = False
        self.ftdi.close()


if __name__ == '__main__':
    # Basic example
    dmx = Interface()
    universe = bytearray([0] * 513)
    start_time = time.time()

    while True:
        _elapsed = time.time() - start_time

        universe[1] = int(255 * (0.5 * math.cos(_elapsed * math.pi * 0.25) + 0.5))
        universe[2] = int(255 * (0.5 * math.cos(_elapsed * math.pi * 0.25 + math.pi) + 0.5))

        dmx.stream(universe)
        time.sleep(1 / float(FRAMERATE))
