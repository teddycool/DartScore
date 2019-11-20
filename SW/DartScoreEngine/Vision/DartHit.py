from cv2 import cv2

from DartScoreEngine.DartScoreEngineConfig import dartconfig


class DartHit(object):

    def __init__(self):
        return

    def initialize(self,hitframe, boundingrect):
        self._hitframe = hitframe
        self._brect = boundingrect
        self._seqno = 0


    def update(self):
        #Find actual hitpoint and mark with a spot
        return

    def draw(self,frame):
        if dartconfig["DartHit"]["WriteFramesToSeparateFiles"]:
            cv2.imwrite("dhframe"+str(self._seqno)+".jpg",frame)
            self._seqno=self._seqno+1
        return frame