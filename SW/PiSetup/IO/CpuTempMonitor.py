__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore

# Purpose of this file:
# Measurre the temperature in the processor
# REF: https://lb.raspberrypi.org/forums/viewtopic.php?t=185244

import subprocess
import time

class CpuTempMonitor(object):

    def __init__(self, mtimeout=10):
        print ("Init cpu temp monitoring")
        self._timeout = mtimeout
        self._lastmeassure = None
        self._lastmtime = 0

    def initialize(self):
        self._meassure()

#Read cpu temp
    def update(self):
        #get cpu temperature using vcgencmd
        if time.time() - self._lastmeassure > self._timeout:
            self._meassure()
        return self._lastmeassure

    def _meassure(self):
        process = subprocess.Popen(['vcgencmd', 'measure_temp'], stdout=subprocess.PIPE)
        output, _error = process.communicate()
        t = str(output).split('=')[1].split('.')[0]
        self._lastmeassure = int(t)  # Return temperature like 43
        self._lastmtime = time.time()



if __name__ == '__main__':
    print ("Testcode for Cpu Temp Monitor")
    tm = CpuTempMonitor(5)
    tm.initialize()
    print (tm.update())
