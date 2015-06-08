__author__ = 'psk'

# Put up the camera, run calibrate
# Start to play...
import os, sys, pygame
from pygame.locals import *
from VideoCapture import Device
import pygame.camera
import Inputs
from GuiComponents import Button
from GuiComponents import Icon

import MainLoop


class Main(object):

    def __init__(self, width, height):
        print "Init Main object..."

        self.dwidth = width
        self.dheight = height
        self.camId=camid
        self._mainLoop=MainLoop.MainLoop()


    def run(self):
        #Init and set up variables...
        print "Init pygame..."
        pygame.init()
        print "Setup screen"
        self.screen = pygame.display.set_mode((self.dwidth,self.dheight))
        self._mainLoop.initialize()
        self.size=(self.dwidth, self.dheight)

        black = 0, 0, 0
        #Init gamestate
        stopped = False
        running=True
        while not stopped:
            black=0,0,0
            self.screen.fill(black)
            self._mainLoop.update(self.screen)
            self._mainLoop.draw(self.screen)
            pygame.display.flip()



#Testcode to run module. Standard Python way of testing modules.
#OBS !! comment out   line 47: "C:\Python27\Lib\site-packages\pygame\_camera_vidcapture.py":
#       #self.dev.setresolution(width, height) on row 49 in:
#
if __name__ == "__main__":
    #Set to webcam ID, std is 0. Networkedcam is probably 1
    camid=1
    #Set size of screen/window
    width= 800
    height=600
    gl=Main(width,height)
    gl.run()
