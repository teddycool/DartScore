__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore

# Purpose of this file:
# Managing the fans to cool down cpu and 'machineroom'

import time
class FanControl(object):

    def __init__(self, GPIO, outputpin):
        self._gpio = GPIO
        self._outputpin = outputpin
        self._running = False

    def initialize(self):
        self._gpio.setup(self._outputpin, self._gpio.OUT, initial=0)


    def update(self):
        pass


    def fancontrol(self, on):
        if on:
            print("FanControl activated for IO: " + str(self._outputpin))
        self._gpio.output(self._outputpin, on)
        self._running = on

    def __del__(self):
        self.fancontrol(False)
        print ("Fancontrol object deactivated and deleted for IO: " + str(self._outputpin))


if __name__ == '__main__':
    print("FanControl test")
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)

    fc1 = FanControl(GPIO, 18)
    fc1.initialize()
    fc2 = FanControl(GPIO, 16)
    fc2.initialize()

    while True:
        fc1.fancontrol(True)
        fc2.fancontrol(False)
        time.sleep(5)
        fc1.fancontrol(True)
        fc2.fancontrol(True)
        time.sleep(10)
        fc1.fancontrol(False)
        fc2.fancontrol(True)
        time.sleep(5)


