__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore

# Purpose of this file:
#  # GUI for the the play state

import sys
sys.path.append("/home/pi/DartScore/SW")

from cv2 import cv2
import pygame
import numpy

from FrontEnd import FrontEndBase

class GameFrontEnd(FrontEndBase.FrontEndBase):

    def __init__(self):
        super(GameFrontEnd, self).__init__()

        self.size=(self.width, self.heigth)
        #self.screen = pygame.display.set_mode((self.width,self.heigth),pygame.FULLSCREEN|pygame.DOUBLEBUF)
        self._myreallybigfont = pygame.font.SysFont("Comic", 150)
        self._mybigfont = pygame.font.SysFont("Comic", 100)
        self._dslabel = self._myreallybigfont.render("* DartScore *", 3, (0, 255, 0))
        self._p1label  = self._mybigfont.render("Player 1", 3, (255, 0, 0))
        self._p2label = self._mybigfont.render("Player 2", 3, (0, 0, 255))

        #TODO: Put the player and score info in a dictionary and loop over the instances

        self._scorep1_1 = self._mybigfont.render("Dart 1: ", 3, (0, 255, 0))
        self._scorep1_2 = self._mybigfont.render("Dart 2: ", 3, (0, 255, 0))
        self._scorep1_3 = self._mybigfont.render("Dart 3: ", 3, (0, 255, 0))

        self._scorep2_1 = self._mybigfont.render("Dart 1: ", 3, (0, 255, 0))
        self._scorep2_2 = self._mybigfont.render("Dart 2:", 3, (0, 255, 0))
        self._scorep2_3 = self._mybigfont.render("Dart 3:", 3, (0, 255, 0))
        self._scorep1_t = self._mybigfont.render("Total: ", 3, (0, 255, 0))
        self._scorep2_t = self._mybigfont.render("Total: ", 3, (0, 255, 0))

        self._p1s1 = " - "
        self._p1s2 = " - "
        self._p1s3 = " - "




    def draw(self, frame):
        frame = numpy.rot90(frame)
        frame = numpy.flipud(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = pygame.surfarray.make_surface(frame)
        black = 0, 0, 0
        self.screen.fill(black)
        self.screen.blit(frame, (590, 200))
        self.screen.blit(self._dslabel, (500, 20))

        # TODO: Use the player/score dictionary and loop over the instances
        self.screen.blit(self._p1label, (100, 70))
        self.screen.blit(self._p2label, (1200, 70))
        self.screen.blit(self._scorep1_1, (100, 250))
        self.screen.blit(self._scorep1_2, (100, 350))
        self.screen.blit(self._scorep1_3, (100, 450))
        # self.screen.blit(self._scorep2_1, (1200, 250))
        # self.screen.blit(self._scorep2_2, (1200, 350))
        # self.screen.blit(self._scorep2_3, (1200, 450))
        self.screen.blit(self._scorep1_t, (100, 550))
        # self.screen.blit(self._scorep2_t, (1200, 550))
        pygame.display.flip()


    def update(self, stateinfostruct): # {"player1": {"d1": "-", "d2": "-", "d3": "-", "set": "-" , "total": "-", "diff": "-", "done": False}}
        self._p1s = stateinfostruct["player1"]
        # TODO: Update the player and score info with the current scores to the dictionary and loop over the instances
        self._scorep1_1 = self._mybigfont.render("Dart 1: " + str(self._p1s["d1"]), 3, (0, 255, 0))
        self._scorep1_2 = self._mybigfont.render("Dart 2: " + str(self._p1s["d2"]), 3, (0, 255, 0))
        self._scorep1_3 = self._mybigfont.render("Dart 3: " + str(self._p1s["d3"]), 3, (0, 255, 0))
        self._scorep1_t = self._mybigfont.render("Total: " + str(self._p1s["total"]), 3, (0, 255, 0))

    def __del__(self):
        pass



#Testcode to run module. Standard Python way of testing modules.
# 1680x1050 (16:10)
#
if __name__ == "__main__":
    import Cam
    import numpy as np
    from DartScoreEngine.Utils import testutils
    cap = Cam.createCam("STREAM")
    cap.initialize('http://192.168.1.131:8081')
    transform = np.float32( [[1.78852294e+00, -1.10143263e-01, -4.85063747e+02],
                             [2.17855239e-01, 1.03682933e+00, -3.82665632e+01],
                             [1.28478485e-03, -1.58506840e-04, 1.00000000e+00]])

    cap.settransformmatrix(transform)
    gl=GameFrontEnd()
    stopped = False
    score = 0
    while not stopped:    # Capture frame-by-frame
        frame = cap.update()
        gl.update(score)
        gl.draw(frame)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                stopped = True

    pygame.quit()