__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore

# Purpose of this file:
#  

import os, sys
#import pygame as pygame
from cv2 import cv2
import pygame
from pygame.locals import *
import numpy
#from DartScore.FrontEnd.FrontEndConfig import config


class FrontEnd(object):

    def __init__(self, width, height):
        print ("Init pygame...")
        self.width = width
        self.heigth = height
        #Init and set up variables...
        pygame.init()

        self.size=(self.width, self.heigth)
        self.screen = pygame.display.set_mode((1024,768),0 )
        self._myfont = pygame.font.SysFont("Arial", 60)
        self._label = self._myfont.render("Hello World !!", 1, (255,0,0))


        #Set surface to handle a frame from camera
        self._snapshot = pygame.Surface(self.size)


    def draw(self, frame):
        frame = numpy.rot90(frame)
        frame = numpy.flipud(frame)
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
                if event.type == pygame.event.QUIT: sys.exit()
                if(event.type is pygame.event.MOUSEBUTTONDOWN):
                    pos = pygame.mouse.get_pos()





#Testcode to run module. Standard Python way of testing modules.
#OBS !! comment out   line 47: "C:\Python27\Lib\site-packages\pygame\_camera_vidcapture.py":
#       #self.dev.setresolution(width, height) on row 49 in:
#
if __name__ == "__main__":

    from DartScoreEngine.Utils import testutils

    cap = testutils.GetTestVideoCapture()
    if (cap.isOpened()== False): 
        print("Error opening video stream or file")
    
    cv2.namedWindow('Video', cv2.WINDOW_AUTOSIZE)
    # Read until video is completed
    #Set to resolution of your webcam
    width=1024
    height=768
    gl=FrontEnd(width, height)

    while(cap.isOpened()):    # Capture frame-by-frame
                    
        ret, frame = cap.read()
        gl.draw(frame)
