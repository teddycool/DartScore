__author__ = 'teddycool'

#Handles io-inputs from lockless momentary buttons mounted on the camera-case
#The button is 'on' when holded depressed
#Types of signals/states: released, pressed and long-pressed, times for holding are defined in config


import DartScoreConfig
import time


class PushButton(object):
    def __init__(self, GPIO, inputpin):
        self._gpio = GPIO
        self._inputpin = inputpin
        self._pressed = False
        self._lastpress = False
        self._states = ["Released","Pressed", "LongPressed"]

    def initialize(self):
        return

    def update(self):
        self._lastpress = self._pressed



    def draw(self, frame):
        return frame

