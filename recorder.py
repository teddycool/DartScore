__author__ = 'teddycool'
# Help utility to record testfiles using project classes
# Set up config as usually and run this file to record the videostream without any texts

from Vision import Vision
import time
import sys

from Recorder import Recorder


class RecorderLoop(object):
    def __init__(self):
        self._vision= Vision.Vision()
        self._rec = Recorder.Recorder()

    def initialize(self):
        print "Main init..."
        self.time=time.time()
        self._rec.initialize()
        self._vision.initialize()
        self._lastframetime = time.time()


    def update(self,rec):
        frame = self._vision.update()
        print self._rec.update(rec)
        return frame

    def draw(self, frame):
        start = time.time()
        framerate = round(1/(time.time()-self._lastframetime),2)
        self._lastframetime= time.time()
        frame = self._rec.draw(frame, int(framerate))
        self._vision.draw(frame, framerate)


#Run this file to start recording to a videofile
if __name__ == "__main__":
    print "Init Main object..."
    recLoop=RecorderLoop()
    recLoop.initialize()
    try:
        while 1:
            frame = recLoop.update(True)
            recLoop.draw(frame)
    except:

        frame = recLoop.update(False)
        recLoop.draw(frame)
        frame= recLoop.update(False)
        recLoop.draw(frame)
        e = sys.exc_info()
        for l in e:
            print l

