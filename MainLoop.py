__author__ = 'teddycool'
#State-switching and handling of general rendering
from Inputs import Inputs
import pygame
from Board import Board
from Cam import Cam
import time
from  StateLoops import CamCalibrateLoop, CamMoutningLoop, PlayStateLoop

class MainLoop(object):
    def __init__(self):
        self._inputs=Inputs.Inputs(self)
        self._board = Board.Board()
        self._calibrateState = CamCalibrateLoop.CamCalibrateLoop()
        self._mountingState = CamMoutningLoop.CamMountingLoop()
        self._playState = PlayStateLoop.PlayStateLoop()
        self._state = {"MountState": self._mountingState, "CalState": self._calibrateState, "PlayState": self._playState}
        self._currentStateLoop = self._state["PlayState"]

    def initialize(self):
        print "Main init..."
        self._inputs.initialize()
        self.time=time.time()
        #Init all states
        for key in self._state.keys():
            self._state[key].initialize()
        print "Game started at ", self.time

    def update(self,screen):
        pos = self._inputs.update()
        return pos

    def draw(self, screen):
        #Move partly to StateLoops
        self._inputs.draw(screen)
        #self._board.draw(screen)


    def changeState(self, newstate):
        if (newstate == 0) or (newstate == "InitState"):
            self._currentStateLoop = CamCalibrateLoop.CamCalibrateLoop()

        self._currentStateLoop.initialize()
        return newstate