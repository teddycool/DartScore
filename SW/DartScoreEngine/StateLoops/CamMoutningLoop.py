__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore
#
# Purpose of this file:

#State handling mounting of cam showing a square in the videofeed  where to have bulls-eye
import sys

sys.path.append("/home/pi/DartScore/SW")

from cv2 import cv2

from DartScoreEngine.DartScoreEngineConfig import dartconfig
from DartScoreEngine.StateLoops import StateLoop
from FrontEnd import FrontEndBase
import time


class CamMountingLoop(StateLoop.StateLoop):
    def __init__(self):
        super(CamMountingLoop, self).__init__()
        return

    def initialize(self):

        width, height= dartconfig['cam']['res']
        aimx = dartconfig['mounting']['aimrectx']
        aimy = dartconfig['mounting']['aimrecty']

        self._startpos= (int(width/2-aimx/2),int(height/2-aimy/2))
        self._centerRect = (int(self._startpos[0]+aimx), int(self._startpos[1]+aimy))
        self._center = (int(width/2),int(height/2))
        self._gui = FrontEndBase.createfrontend("Mount")

    def update(self, frame, context):
        #TODO: add logic for reading input and switch state
        self._gui.update(None)
        return frame

    def draw(self, frame):
        cv2.rectangle(frame, self._startpos, self._centerRect, dartconfig['color']['aim'], 5)
        cv2.putText(frame,"Mount to fit bullseye inside the box", (self._center[0]+15,self._center[1]),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        cv2.line(frame, self._center, (self._center[0],0), dartconfig['color']['bullseye'], 2)
        cv2.putText(frame,"Put this line inside the 20-sector", (self._center[0]-100,100),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        cv2.putText(frame,"Mounting State", (5,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        cv2.putText(frame,"Press any key when ready", (5,40),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        self._gui.draw(frame)
        return frame



if __name__ == "__main__":
    import sys
    import pygame

    sys.path.append("/home/pi/DartScore/SW")

    from DartScoreEngine.Utils import DummyMainLoop

    context = DummyMainLoop.DummyMainLoop()

    loop = CamMountingLoop()
    loop.initialize()
    stopped = False
    while not stopped:
        frame = context._cam.update()
        loop.update(frame, context)
        loop.draw(frame)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                stopped = True

    pygame.quit()
