__author__ = 'teddycool'
#State handling the actual game, might be separated to several states


import cv2

from Actuators import LedIndicator
from DartScoreEngineConfig import dartconfig
from  StateLoop import StateLoop
from Vision import DartDetector

class PlayStateLoop(StateLoop):
    def __init__(self):
        super(PlayStateLoop, self).__init__()
        return

    def initialize(self ):
        print "PlayState init..."
  #      self._gpio=gpio
        self._dartDetectorFrames = 0
        self._init = False
        self._empty = True
        self._warmup = 0
   #     self._hitLed = LedIndicator.LedIndicator(self._gpio, dartconfig["IO"]["HitLed"])

    def update(self, frame):
  #      self._hitLed.update()
        #TODO: move to calibrate state
        if self._warmup < dartconfig["play"]["warmupframes"]:
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
                    print "New dart or change detected in this frame"
                    #Add calculation of hit-scores here
                    self._dartDetectorFrames = 0
                    self._previousFrame = frame.copy()
 #                   self._hitLed.activate(True)
                else:
                    self._dartDetectorFrames = self._dartDetectorFrames + 1
                    if self._dartDetectorFrames > dartconfig["play"]["hitframes"]:
                        self._dartDetectorFrames = 0
                        #This was an actual hit, add sum of hit-scores  for player here
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
                cv2.putText(frame,"Board empty", (5,50),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
            else:
                cv2.putText(frame,"Board not empty", (5,50),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
                frame = self._dartDetector.draw(frame)

            cv2.putText(frame,"Play State", (5,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        else:
            cv2.putText(frame,"Play State - warming up", (5,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        return frame