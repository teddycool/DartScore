__author__ = 'teddycool'

#Handles io-inputs from lockless momentary buttons mounted on the camera-case
#The button is 'on' when holded depressed
#Types of signals/states: released, pressed and long-pressed, times for holding are defined in config

from DartScoreConfig import dartconfig
import time
import cv2


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


if __name__ == '__main__':
    import RPi.GPIO as GPIO
    cal = PushButton(GPIO, 23)
    cal.initialize()
    game = PushButton(GPIO, 24)
    game.initialize()
    try:
        while True:
            print str(time.time()) + " Cal: " + str(cal.update()) + " Game: " + str(game.update())
            time.sleep(0.2)
    except:
        GPIO.cleanup()
