_author__ = 'teddycool'
#State handling mounting of cam showing a square in the videofeed  where to have bulls-eye


import cv2

from DartScoreEngine.DartScoreEngineConfig import dartconfig
from  StateLoop import StateLoop
import time


class CamMountingLoop(StateLoop):
    def __init__(self):
        super(CamMountingLoop, self).__init__()
        return

    def initialize(self):

        width, height= dartconfig['cam']['res']
        aimx = dartconfig['mounting']['aimrectx']
        aimy = dartconfig['mounting']['aimrecty']

        self._startpos= (width/2-aimx/2,height/2-aimy/2)
        self._centerRect = (self._startpos[0]+aimx, self._startpos[1]+aimy)
        self._center = (width/2,height/2)
        self._currentFrame = None
        self._previousFrame = None

    def update(self, frame):
        if self._previousFrame == None:
            self._priviousFrame = frame
            self._currentFrame = frame.copy()
        else:
            self._priviousFrame = self._currentFrame
            self._currentFrame = frame.copy()


        #TODO: Add logic to switch state when ready Ie a button on the cam


        return frame

    def draw(self, frame):
        cv2.rectangle(frame, self._startpos, self._centerRect, dartconfig['color']['aim'], 5)
        cv2.circle(frame, self._center, 10, dartconfig['color']['bullseye'], 2)
        cv2.putText(frame,"Mount to match bullseye here", (self._center[0]+15,self._center[1]),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        cv2.line(frame, self._center, (self._center[0],0), dartconfig['color']['bullseye'], 2)
        cv2.putText(frame,"Put this line inside the 20-sector", (self._center[0]-100,100),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        cv2.putText(frame,"Mounting State", (5,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        cv2.putText(frame,"Press cal-button when ready", (5,40),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

        return frame