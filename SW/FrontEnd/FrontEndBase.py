__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore
#
# Purpose of this file:
# Base class for frontends
import sys
sys.path.append("/home/pi/DartScore/SW")


import pygame
import numpy as np
import time

from DartScoreEngine.StateLoops import CamMoutningLoop
from DartScoreEngine.StateLoops import CamCalibrateLoop
from DartScoreEngine.StateLoops import PlayStateLoop

def createfrontend(statetype):
    if statetype =="Calibrate":
        from FrontEnd import CalibrationFrontEnd
        frontend  = CalibrationFrontEnd.CalibrationFrontEnd()
        return frontend
    if statetype == "Play":
        from FrontEnd import GameFrontEnd
        frontend  = GameFrontEnd.GameFrontEnd()
        return frontend
    if statetype == "Mount":
        from FrontEnd import CalibrationFrontEnd
        frontend  = CalibrationFrontEnd.CalibrationFrontEnd()
        return frontend

    raise ("FrontEndSelectionError")



class FrontEndBase(object):

    def __init__(self, w=1680, h=1050):
       # print("Init pygame...")
        self.width = w
        self.heigth = h
        # Init and set up variables...

        pygame.init()

        self.size = (self.width, self.heigth)
        self.screen = pygame.display.set_mode((self.width,self.heigth),pygame.FULLSCREEN|pygame.DOUBLEBUF)

        # Set surface to handle a frame from camera
        self._snapshot = pygame.Surface(self.size)

    def initialize(self):
        return

    def update(self, stateinfostruct):
        return

    def draw(self, frame):
        return


