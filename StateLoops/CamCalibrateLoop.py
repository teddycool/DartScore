__author__ = 'teddycool'
#State handling calibration of cam at startup when mounted correctly
#Warm-up, set exposure etc, read dartboard and setup the 'score-calculator-engine'

from Board import Board
from Board import BoardArray
from  StateLoop import StateLoop


class CamCalibrateLoop(StateLoop):
    def __init__(self):
        super(CamCalibrateLoop, self).__init__()
        return

    def initialize(self):

        return

    def update(self, screen):
        return screen

    def draw(self, snapshot):

        return snapshot