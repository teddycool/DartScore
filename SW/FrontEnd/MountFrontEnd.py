__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore
#
# Purpose of this file:
# GUI for the the mounting state

import sys
sys.path.append("/home/pi/DartScore/SW")

from cv2 import cv2
import pygame
import numpy

from FrontEnd import FrontEndBase

class GameFrontEnd(FrontEndBase.FrontEndBase):

    def __init__(self):
        super(GameFrontEnd, self).__init__()
        self._myreallybigfont = pygame.font.SysFont("Comic", 150)
        self._mybigfont = pygame.font.SysFont("Comic", 100)
        self._dslabel = self._myreallybigfont.render("* DartScore *", 3, (0, 255, 0))



    def update(self, frame, stateinfostruct):
        pass


    def draw(self, frame):
        frame = numpy.rot90(frame)
        frame = numpy.flipud(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = pygame.surfarray.make_surface(frame)
        black = 0, 0, 0
        self.screen.fill(black)
        self.screen.blit(frame, (300, 200))
        self.screen.blit(self._dslabel, (500, 20))
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

    gl=GameFrontEnd()
    stopped = False
    while not stopped:    # Capture frame-by-frame
        frame = cap.update()
        gl.update(None)
        gl.draw(frame)
        event = pygame.event.wait()
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            stopped = True
    pygame.quit()