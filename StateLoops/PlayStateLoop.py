__author__ = 'teddycool'
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

    def update(self, frame):
        if not self._init:
            self._dartDetector = DartDetector.DartDetector(frame)
            self._previousFrame = frame
            self._init = True
        else:
            if not self._dartDetector.boardEmpty(frame):
                self._empty = False
                if self._dartDetector.detectDart(frame, self._previousFrame):
                    self._dartDetectorFrames = 0
                    self._previousFrame = frame
                    frame = self._dartDetector.draw(frame)
                else:
                    self._dartDetectorFrames = self._dartDetectorFrames + 1
                if self._dartDetectorFrames > 5:
                    frame = self._dartDetector.draw(frame)
            else:
                self._empty = True
                self._dartDetectorFrames = 0
                self._previousFrame = frame

        return frame

    def draw(self, frame):
        if self._empty:
            cv2.putText(frame,"Board empty", (200,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        else:
            cv2.putText(frame,"Board not empty", (200,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

        cv2.putText(frame,"PlayState", (5,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        return frame