__author__ = 'teddycool'

#Handles io-inputs from  buttons and switches mounted on the case


#TODO: fix raise exception at unlogical states...

try:
    from DartScoreConfig import dartconfig
except:
    dartconfig = {"Button": {"Pressed": 0.1, "LongPressed": 1.5}}
import time

import cv2


#The button is 'on' when holded pressed and IO defined in init is connected to ground
#Types of signals/states: released, pressed and long-pressed, times for holding are defined in config
class PushButton(object):
    def __init__(self, GPIO, inputpin):
        self._gpio = GPIO
        self._inputpin = inputpin
        self._pressed = False
        self._lastpress = False
        self._states = ["Released","Pressed", "LongPressed"]

    def initialize(self):
        self._gpio.setmode(self._gpio.BCM)
        self._gpio.setup(self._inputpin, self._gpio.IN, pull_up_down=self._gpio.PUD_UP)

    def update(self):
        self._state = self._states[0]
        if self._gpio.input(self._inputpin) == False: #Button pressed, PullUp is released
            self._pressed = True
            if self._lastpress != self._pressed: #First round
                self._presstime = time.time()
                self._lastpress = self._pressed
            else:
                if time.time() - self._presstime > dartconfig["Button"]["LongPressed"]:
                    self._state = self._states[2]
                else:
                    if time.time() - self._presstime > dartconfig["Button"]["Pressed"]:
                        self._state = self._states[1]
        else:
            self._pressed= False
            self._lastpress = self._pressed
        return self._state


    def draw(self, frame, name, x, y):
        cv2.putText(frame,"Button " + name + ": " + str(self._state), (x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        print "Button " + name + ": " + str(self._state)
        return frame

#The switch is 'on' when IO defined in init is connected to ground
class OnOffSwitch(object):
    def __init__(self, GPIO, inputpin):
        self._gpio = GPIO
        self._inputpin = inputpin
        self._states = ['OFF', 'ON']
        self._state = self._states[0]

    def initialize(self):
        self._gpio.setmode(self._gpio.BCM)
        self._gpio.setup(self._inputpin, self._gpio.IN, pull_up_down=self._gpio.PUD_UP)

    def update(self):
        if not self._gpio.input(self._inputpin): #When grounded, switch is on, PullUp is released
            self._state= self._states[1]
        else:
            self._state = self._states[0]
        return self._state


    def draw(self, frame, name, x, y):
        cv2.putText(frame,"OnOffSwitch " + name + ": " + str(self._state), (x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        print "OnOffSwitch " + name + ": " + str(self._state)
        return frame


class OnOffOnSwitch(object):
    def __init__(self, GPIO, inputpin1, inputpin2):
        self._gpio = GPIO
        self._inputpin1 = inputpin1
        self._inputpin2 = inputpin2
        self._states = ['OFF', 'ON1','ON2']
        self._state = self._states[0]

    def initialize(self):
        self._gpio.setmode(self._gpio.BCM)
        self._gpio.setup(self._inputpin1, self._gpio.IN, pull_up_down=self._gpio.PUD_UP)
        self._gpio.setup(self._inputpin2, self._gpio.IN, pull_up_down=self._gpio.PUD_UP)

    def update(self):
        if self._gpio.input(self._inputpin1) and self._gpio.input(self._inputpin2):
            self._state = self._states[0]
        else:
            if self._gpio.input(self._inputpin1) and  not self._gpio.input(self._inputpin2):
                self._state = self._states[2]
            if not self._gpio.input(self._inputpin1) and self._gpio.input(self._inputpin2):
                self._state = self._states[1]
        return self._state

    def draw(self, frame, name, x, y):
        cv2.putText(frame,"OnOffOnSwitch " + name + ": " + str(self._state), (x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        print "OnOffOnSwitch " + name + ": " + str(self._state)
        return frame

class OnOnSwitch(object):
    def __init__(self, GPIO, inputpin1, inputpin2):
        self._gpio = GPIO
        self._inputpin1 = inputpin1
        self._inputpin2 = inputpin2
        self._states = ['OFF', 'ON1','ON2']
        self._state = self._states[0]

    def initialize(self):
        self._gpio.setmode(self._gpio.BCM)
        self._gpio.setup(self._inputpin1, self._gpio.IN, pull_up_down=self._gpio.PUD_UP)
        self._gpio.setup(self._inputpin2, self._gpio.IN, pull_up_down=self._gpio.PUD_UP)

    def update(self):
        if self._gpio.input(self._inputpin1) and self._gpio.input(self._inputpin2):
            self._state = self._states[0]
        else:
            if self._gpio.input(self._inputpin1) and  not self._gpio.input(self._inputpin2):
                self._state = self._states[2]
            if not self._gpio.input(self._inputpin1) and self._gpio.input(self._inputpin2):
                self._state = self._states[1]
        return self._state


    def draw(self, frame, name, x, y):
        cv2.putText(frame,"OnOffOnSwitch " + name + ": " + str(self._state), (x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        print "OnOffOnSwitch " + name + ": " + str(self._state)
        return frame



if __name__ == '__main__':
    import RPi.GPIO as GPIO
    cal = PushButton(GPIO, 23)
    cal.initialize()
    game = PushButton(GPIO, 24)
    game.initialize()
    try:
        while True:
            print str(time.time()) + " Cal: " + str(cal.update()) + " Game: " + str(game.update())
            time.sleep(0.1)
    except:
        GPIO.cleanup()