__author__ = 'teddycool'
#State handling the actual game, might be separated to several states


import cv2

from  StateLoop import StateLoop
from Vision import DartDetector

class PlayStateLoop(StateLoop):
    def __init__(self):
        super(PlayStateLoop, self).__init__()
        return

    def initialize(self ):
        print "PlayState init..."
        self._dartDetectorFrames = 0
        self._init = False
        self._empty = True
        self._warmup = 0

    def update(self, frame):
        if self._warmup < 10:
            self._warmup = self._warmup + 1
            return frame

        if not self._init:
            self._dartDetector = DartDetector.DartDetector(frame)
            self._previousFrame = frame.copy()
            self._init = True
            print "First frame (empty board) initialized in PlayState Loop.."
        else:
            if not self._dartDetector.boardEmpty(frame):
                print "Detected not empty"
                self._empty = False
                if self._dartDetector.detectDart(frame, self._previousFrame):
                    print "New dart detected in this frame"
                    self._dartDetectorFrames = 0
                    self._previousFrame = frame.copy()
                else:
                    self._dartDetectorFrames = self._dartDetectorFrames + 1
                    if self._dartDetectorFrames > 10:
                        self._dartDetectorFrames = 0
                        #self._previousFrame = frame.copy()
            else:
                print "Detected empty"
                self._empty = True
                self._dartDetectorFrames = 0
                self._previousFrame = frame.copy()
        print "Similar frames with darts detected: " + str(self._dartDetectorFrames)
        return frame

    def draw(self, frame):
        if self._init:
            if self._empty:
                cv2.putText(frame,"Board empty", (200,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
            else:
                cv2.putText(frame,"Board not empty", (200,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
                frame = self._dartDetector.draw(frame)

            cv2.putText(frame,"PlayState", (5,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        else:
            cv2.putText(frame,"PlayState - warming up", (5,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        return frame