__author__ = 'teddycool'
#State handling calibration of cam at startup when mounted correctly
#Warm-up, set exposure etc, read dartboard and setup the 'score-calculator-engine'

from Board import Board
from Board import BoardArray
from  StateLoop import StateLoop
import cv2


class CamCalibrateLoop(StateLoop):
    def __init__(self):
        super(CamCalibrateLoop, self).__init__()
        return

    def initialize(self):
        return

    def update(self, frame):
        return frame

    def draw(self, frame):
        cv2.putText(frame,"Calibrate State", (5,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        return frame