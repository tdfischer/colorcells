#!/usr/bin/env python
import serial
import logging
import datetime
import time

class Sign(object):
    def __init__(self, device):
        self._ser = serial.Serial(device, baudrate=300, stopbits=2)
        self._log = logging.getLogger("colorcell")

    def send(self, data):
        self._ser.write(chr(data))
        ret = ord(self._ser.read())
        if (ret != data):
            raise IOError, "Expected %s, got %s"%(data.encode("hex"), ret.encode("hex"))

    def text(self, text):
        for c in str(text):
            self.send(ord(c))

    def stop(self):
        self.send(1)

    def run(self):
        self.send(13)

    def speed(self, speed):
        self.send(2)
        self.send(ord('0')+speed)

    def beep(self):
        self.send(7)

    def pause(self):
        self.send(6)

    def clear(self):
        self.send(14)

    def sequence(self, sequence):
        self.send(4)
        for s in sequence:
            self.send(s+1)
        self.stop()

    def program(self, cell):
        assert(cell >= 0)
        assert(cell <= 9)
        self.send(9)
        self.text(int(cell))

    EFFECT_WIPE_DOWN = 27
    EFFECT_WIPE_UP = 26
    EFFECT_BIG = 16

    def effect(self, effect):
        if (effect == Sign.EFFECT_WIPE_DOWN):
            self.send(27)
        if (effect == Sign.EFFECT_WIPE_UP):
            self.send(26)
        if (effect == Sign.EFFECT_BIG):
            self.send(16)

    def speed(self, speed):
        self.send(2)
        self.send(ord('0')+int(speed))

    def graphic(self, graphic):
        self.send(30)
        self.send(ord('a')+int(graphic))

    def setTime(self, now=datetime.datetime.now().time()):
        self.send(23)
        hour = now.hour%12
        if (hour < 10):
            hour = "0%d"%hour
        minute = now.minute
        if (minute < 10):
            minute = "0%d"%minute
        self.text('%s%s'%(hour, minute))
        time.sleep(1)
        if (now.hour > 12):
            self.text("n")
        else:
            self.text("y")

    COLOR_RED = 97
    COLOR_ORANGE = 98
    # 99 is also yellow, but only for the foreground
    COLOR_LIME = 100
    COLOR_GREEN = 101
    COLOR_BLACK = 102
    COLOR_YELLOW = 103

    def foreground(self, color):
        self.send(21)
        self.send(color)

    def background(self, color):
        self.send(22)
        self.send(color)

    def wipe(self):
        for i in range(0, 10):
            self.program(i)
            self.clear()

    def reset(self):
        self.stop()
        self.setTime()
        self.wipe()
        self.program(0)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    s = Sign("/dev/ttyUSB3")
    s.stop()
    s.reset()
    s.program(0)
    s.speed(7)
    s.clear()
    s.text("Graphics test: ")
    s.foreground(Sign.COLOR_GREEN)
    s.background(Sign.COLOR_RED)
    for i in range(0, 17):
        s.text(i)
        s.graphic(i)
        s.text("  ")
    s.program(1)
    for i in range(0, 7):
        for j in range(0, 7):
            s.foreground(ord('a')+i)
            s.background(ord('a')+j)
            s.text("Color %d-%d "%(i, j))
    s.run()
