__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore

# Purpose of this file:
#Handles the buttons. Each button has also a light

import time

class ArchadeButton(object):
    def __init__(self, GPIO, inputpin, outputpin, pt, lpt):
        self._gpio = GPIO
        self._inputpin = inputpin
        self._outputpin = outputpin
        self._bpressed = False
        self._blastpress = False
        self._bstates = ["Released","Pressed", "LongPressed"]
        self._lit = False
        self._lastli = False
        self._shortpresstime = pt
        self._longpresstime = lpt

    def initialize(self):
        self._gpio.setup(self._inputpin, self._gpio.IN, pull_up_down=self._gpio.PUD_DOWN)
        self._gpio.setup(self._outputpin, self._gpio.OUT, initial=0)

    def update(self):
        self._bstate = self._bstates[0]
        if self._gpio.input(self._inputpin) == False:  # Button pressed, PullUp is released
            self._pressed = True
            if self._lastpress != self._pressed:  # First round
                self._presstime = time.time()
                self._lastpress = self._pressed
            else:
                if time.time() - self._presstime > self._longpresstime:
                    self._bstate = self._bstates[2]
                else:
                    if time.time() - self._presstime > self._shortpresstime:
                        self._bstate = self._bstates[1]
        else:
            self._pressed = False
            self._lastpress = self._pressed
        return self._bstate


    def activate(self, on=True):
        if on:
            print ("LedIndicator object activated for IO: " + str(self._outputpin))
        self._gpio.output(self._outputpin, on)


    def __del__(self):
        self.activate(False)
        print ("LedIndicator object deactivated and deleted for IO: " + str(self._outputpin), + " and " + str(self._inputpin))

if __name__ == '__main__':
    print("TestcodeArchadeButton")
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    archades ={}
    archades["GREEN"] = ArchadeButton(GPIO,8,7,0.5, 2)
    archades["YELLOW"] = ArchadeButton(GPIO, 14, 15, 0.5, 2)
    archades["RED"] = ArchadeButton(GPIO, 23, 24, 0.5, 2)
    archades["BLUE"] = ArchadeButton(GPIO, 20, 21, 0.5, 2)

    for button in archades:
        archades[button].initialize()
        archades[button].activate(True)
        time.sleep(1)

    try:
        while True:
            for button in archades:
                state = archades[button].update()
                if  state != "Released":
                    print(button + ": " + state)
            time.sleep(0.1)
    except(KeyboardInterrupt):
        del (GPIO)
