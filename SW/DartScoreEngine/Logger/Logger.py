__author__ = 'teddycool'
import time

class Logger(object):

    def __init__(self, logfile):
        self._log = file(logfile,'rw')

    def log(self, text):
        timestamp = time.time()
        self._log.write(timestamp, text)

    def __del__(self):
        self._log.close()

