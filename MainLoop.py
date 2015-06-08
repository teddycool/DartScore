__author__ = 'psk'
#State-switching and handling of general rendering
from Inputs import Inputs
import pygame
from Board import Board
from Cam import Cam
import time
from  StateLoops import CamCalibrateLoop

class MainLoop(object):
    def __init__(self):
        self._inputs=Inputs.Inputs(self)
        self._board = Board.Board()
        self._cam=Cam.Cam()
        self._currentStateLoop = CamCalibrateLoop.CamCalibrateLoop()
        self._state = {0:"InitState", 1: "PlayState", 2: "MountCamState"}

    def initialize(self):
        print "Main init..."
        self._inputs.initialize()
        self._cam.initialize()
        self._board.initialize((self._cam.width, self._cam.height))
        self.time=time.time()
        print "Game started at ", self.time

    def update(self,screen):
        self._cam.update()
        pos = self._inputs.update()

        return pos

    def draw(self, screen):
        #Move partly to StateLoops

        self._inputs.draw(screen)
        myfont = pygame.font.SysFont("Arial", 20)
        boardlabel = myfont.render("DartBoard" , 1, (255,255,255))
        activeLabel = myfont.render("Active player:", 1, (255,255,255))

        screen.blit(self._cam.csnapshot, (0,0))
        screen.blit(boardlabel, (5,5))
        screen.blit(activeLabel, (645, 50))
        return screen

    def changeState(self, newstate):
        if (newstate == 0) or (newstate == "InitState"):
            self._currentStateLoop = CamCalibrateLoop.CamCalibrateLoop()

        self._currentStateLoop.initialize()
        return newstate