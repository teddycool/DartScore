__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore
#
# Purpose of this file:
# GUI for the calibration state

import sys
sys.path.append("/home/pi/DartScore/SW")

from cv2 import cv2
import pygame
import numpy

from FrontEnd import FrontEndBase

class CalibrationFrontEnd(FrontEndBase.FrontEndBase):

    def __init__(self):
        super(CalibrationFrontEnd, self).__init__()
        self._myreallybigfont = pygame.font.SysFont("Comic", 150)
        self._mybigfont = pygame.font.SysFont("Comic", 100)
        self._dslabel = self._myreallybigfont.render("* DartScore *", 3, (0, 255, 0))
        self._cam1label = self._myreallybigfont.render("Camera 1 stream", 3, (0, 255, 0))
        self._cam2label = self._myreallybigfont.render("Camera 2 stream", 3, (0, 255, 0))



    def update(self, stateinfostruct):
        pass


    def draw(self, frame1, frame2=None):
        black = 0, 0, 0
        frame1 = numpy.rot90(frame1)
        frame1 = numpy.flipud(frame1)
        frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
        frame1 = pygame.surfarray.make_surface(frame1)
        self.screen.fill(black)
        self.screen.blit(frame1, (300, 200))
        self.screen.blit(self._dslabel, (500, 20))
        self.screen.blit(self._cam1label, (300, 900))
        if frame2 != None:
            frame2 = numpy.rot90(frame2)
            frame2 = numpy.flipud(frame2)
            frame2 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
            frame2 = pygame.surfarray.make_surface(frame2)
            self.screen.fill(black)
            self.screen.blit(frame2, (300, 800))
            self.screen.blit(self._dslabel, (500, 20))
           # self.screen.blit(self._cam1label, (300, 900))

        pygame.display.flip()



#Testcode to run module. Standard Python way of testing modules.
# 1680x1050 (16:10)
#
if __name__ == "__main__":
    import Cam
    import numpy as np
    from DartScoreEngine.Utils import testutils
    cap = Cam.createCam("STREAM")
    cap.initialize('http://192.168.1.131:8081')

    gl=CalibrationFrontEnd()
    stopped = False
    while not stopped:    # Capture frame-by-frame
        frame = cap.update()
        gl.update(None)
        gl.draw(frame)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                stopped = True

    pygame.quit()