__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore

# Purpose of this file:
# Read temperature from a 1w DS18B20
#       http://www.modmypi.com/blog/ds18b20-one-wire-digital-temperature-sensor-and-the-raspberry-pi
#       https://it.pinout.xyz/pinout/1_wire
# add this to  /boot/config.txt
# dtoverlay=w1-gpio,gpiopin=16



import os
import time
import cv2

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

class DS18B20(object):
    
    def __init__(self, serial, timeout = 120):
        self._serial = serial
        self._sensorfile= "/sys/bus/w1/devices/" + self._serial + "/w1_slave"
        self._temp= "N/A"
        self._lastUpdate = 0
        self._timeout = timeout

    def initialize(self):
        pass

    def update(self):
        if time.time() - self._lastUpdate > self._timeout:
            self.read_temp()
            self._lastUpdate = time.time()


    def temp_raw(self):
        f = open(self._sensorfile, 'r')
        lines = f.readlines()
        f.close()
        return lines
    
    def read_temp(self):
        try:
            lines = self.temp_raw()
            while lines[0].strip()[-3:] != 'YES':
                lines = self.temp_raw()

            temp_output = lines[1].find('t=')

            if temp_output != -1:
                temp_string = lines[1].strip()[temp_output+2:]
                temp_c = float(temp_string) / 1000.0
                self._temp = str(round(temp_c,1))
        except:
            self._temp=  "N/A"



if __name__ == '__main__':
    print ("Testcode for DS18B20")
    serials = ["28-0516a7c088ff", #Replace...
               ]
    terms = []
    for serial in serials:
        print ("DS18B20 with serial " + serial + " created")
        ts = DS18B20(serial)
        terms.append(ts)

    for ts in terms:
        print(ts.read_temp())
        print(ts.temp_raw())