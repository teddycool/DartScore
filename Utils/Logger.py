__author__ = 'teddycool'
import time

class Logger(object):

    def __init__(self, logfile):
        self._log = logfile

    def log(self, text):
        timestamp = time.time()
        self._log.write(timestamp, text)

