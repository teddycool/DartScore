__author__ = 'teddycool'
#State handling calibration of cam at startup when mounted correctly
#Warm-up, set exposure etc, read dartboard and setup the 'score-calculator-engine'
import sys
import time
import pickle

sys.path.append("/home/pi/DartScore/SW")
from DartScoreEngine.StateLoops import StateLoop
from DartScoreEngine.BoardCalibration import Lines
from DartScoreEngine.BoardCalibration import Sectors
from DartScoreEngine.BoardCalibration import BoardArray
from FrontEnd import FrontEndBase
from DartScoreEngine.DartScoreEngineConfig import dartconfig

from cv2 import cv2
import numpy as np


class CamCalibrateLoop(StateLoop.StateLoop):
    def __init__(self):
        super(CamCalibrateLoop, self).__init__()
        self._lines = Lines.Lines()
        self._sectors = Sectors.Sectors()
        self._firstFrame = None
        self._states = ["BullsEye", "Sectors", "Calpoints", "Transform","View", "Ready"]
        self._state = "BullsEye"
        self._bullseye = None
        self._calcorners = None
        self._tmatrix = []
        #self._gui =
        return

    def initialize(self):
        self._gui = FrontEndBase.createfrontend("Calibrate")

    def update(self, frame, context):
        #TODO: add logic for switching state by pressing a button (first time) after startup and automatically if calibrated between each set.
        if self._state == "BullsEye":
            lines = self._lines.findSectorLines(frame)
            self._bullseye = self._lines.findBullsEye(lines)
            self._state = "Sectors"
        elif self._state == "Sectors":
            contoures = self._sectors.findouterslices(frame, True)
            self._calcorners= self._sectors.findcalcorners(contoures, self._bullseye)
            self._state = "Transform"
        elif self._state == "Transform":
            # TODO: move to sector class and get the matrix as a property
            correct = np.float32([[137, 137], [363, 137], [363, 363], [137, 363]])
            skewed = np.float32([self._sectors._calpointtoppleft, self._sectors._calpointtopright, self._sectors._calpointbottomright,
                                 self._sectors._calpointbottomleft])
            self._tmatrix = cv2.getPerspectiveTransform(skewed, correct)
            # TODO: save calibtration values, -> pickle dump transform matrix...
            pickle.dump(self._tmatrix, open(dartconfig["calibration"]["savepath"], "wb"))
            context._tmatrix=self._tmatrix
            context._cam.settransformmatrix(self._tmatrix)
            self._state = "View"
        elif self._state == "View":
            ba = BoardArray.BoardArray()
            frame = ba.draw(frame)
            self._state = "Ready"
        elif self._state == "Ready":
            context.changeState("PlayState")

    def draw(self, frame):
        if self._state=="Ready":
            cv2.putText(frame, "Calibration ready...  ", (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            frame = self._gui.draw(frame)
            time.sleep(3)
        else:
            cv2.putText(frame, "Calibrate State", (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            if self._bullseye != None:
                cv2.circle(frame, self._bullseye, 5, (0, 0, 255), 4)
            if self._calcorners != None:
                for corner in self._calcorners:
                    cv2.circle(frame, corner, 5, (0, 0, 255), 4)
            cv2.putText(frame, str(self._tmatrix), (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            frame = self._gui.draw(frame)
            time.sleep(1)
        return frame

if __name__ == "__main__":
    from DartScoreEngine.Utils import testutils
    import sys
    import pygame
    sys.path.append("/home/pi/DartScore/SW")

    from DartScoreEngine.Utils import DummyMainLoop
    context = DummyMainLoop.DummyMainLoop()

    cal = CamCalibrateLoop()
    cal.initialize()
    stopped = False
    while not stopped:
        frame = context._cam.update()
        cal.update(frame, context)
        cal.draw(frame)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                stopped = True

    pygame.quit()
