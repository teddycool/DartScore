__author__ = 'psk'
import os, sys, pygame, cv2
from pygame.locals import *
from VideoCapture import Device
import pygame.camera
import numpy
from FrontEndConfig import config


class FrontEnd(object):

    def __init__(self, width, height):
        print "Init pygame..."
        self.width = width
        self.heigth = height
        #Init and set up variables...
        pygame.init()

        self.size=(self.width, self.heigth)
        self.screen = pygame.display.set_mode(config["screen"]["display"],0 )
        self._myfont = pygame.font.SysFont("Arial", 60)
        self._label = self._myfont.render("Hello World !!", 1, (255,0,0))


        #Set surface to handle a frame from camera
        self._snapshot = pygame.surface.Surface(config["screen"]["res"])


    def draw(self, frame):
        frame = numpy.rot90(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = pygame.surfarray.make_surface(frame)
        black = 0, 0, 0
        self.screen.fill(black)
        #pygame.surfarray.blit_array(self._snapshot, frame)
        #self.screen.blit(frame, (0, 0))
        self.screen.blit(frame, (0, 0))
        self.screen.blit(self._label, (100, 200))
        pygame.display.flip()



    def __del__(self):
        pass


    def run(self):

        #Init gamestate
        stopped = False
        while not stopped:

            #Get inputs from user....
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                if(event.type is MOUSEBUTTONDOWN):
                    pos = pygame.mouse.get_pos()





#Testcode to run module. Standard Python way of testing modules.
#OBS !! comment out   line 47: "C:\Python27\Lib\site-packages\pygame\_camera_vidcapture.py":
#       #self.dev.setresolution(width, height) on row 49 in:
#
if __name__ == "__main__":
    #Set to webcam ID, std is 0. Networkedcam is probably 1
    camid=0
    #Set to resolution of your webcam
    width=1280
    height=720

    gl=FrontEnd(width, height, camid)
    gl.run()