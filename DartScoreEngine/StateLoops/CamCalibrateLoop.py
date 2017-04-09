__author__ = 'teddycool'
#State handling calibration of cam at startup when mounted correctly
#Warm-up, set exposure etc, read dartboard and setup the 'score-calculator-engine'

from DartScoreEngine.StateLoops import StateLoop
from DartScoreEngine.Board import Board
import cv2


class CamCalibrateLoop(StateLoop.StateLoop):
    def __init__(self):
        super(CamCalibrateLoop, self).__init__()
        self._board = Board.Board()
        self._firstFrame = None
        return

    def initialize(self):
        #Calculate sectorlines passing bulls-eye
        return

    def update(self, frame):
        if self._firstFrame == None:
            self._first = frame
            frame = self._board.findSectorLines(frame)
        return frame

    def draw(self, frame):
        cv2.putText(frame,"Calibrate State", (5,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        return frame