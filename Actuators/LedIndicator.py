__author__ = 'teddycool'
import time
from WeatherStationConfig import config

class LedIndicator(object):
    def __init__(self, GPIO, controlpin):
        self._gpio = GPIO
        self._pin = controlpin
        self._gpio.setup(self._pin,self._gpio.OUT, initial=0)
        self._lastActivate = time.time()
        print "LedIndicator object created for IO: " + str(self._pin)

    def activate(self, on=True):
        if on:
            print "LedIndicator object activated for IO: " + str(self._pin)
            self._lastActivate = time.time()
        self._gpio.output(self._pin, on)


    def update(self):
        if time.time() - self._lastActivate > config["LedIndicator"]["ActivationTime"]:
            self.activate(False)

    def __del__(self):
        self.activate(False)
        print "LedIndicator object deactivated and deleted for IO: " + str(self._pin)


if __name__ == '__main__':
    print "Testcode for LedIndicators"
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    import time
    led1 = LedIndicator(GPIO, 12)
    led2 = LedIndicator(GPIO, 16)

    led1.activate(True)
    led2.activate(True)
    time.sleep(5)
    led1.activate(False)
    time.sleep(2)
    led2.activate(False)
    GPIO.cleanup()