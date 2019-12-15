__author__ = 'teddycool'
# State handling the actual game, might be separated to several states
# Internal states: start ->
#                           player1 -> player2 -> player1 -> player2....
#                   -> end

import sys

sys.path.append("/home/pi/DartScore/SW")
from cv2 import cv2

from DartScoreEngine.DartScoreEngineConfig import dartconfig
from DartScoreEngine.StateLoops import StateLoop
from DartScoreEngine.Vision import DartDetector
from FrontEnd import FrontEndBase

class PlayStateLoop(StateLoop.StateLoop):
    def __init__(self):
        super(PlayStateLoop, self).__init__()
        return

    def initialize(self ):
        #print ("PlayState init...")
        self._dartDetectorFrames = 0
        self._gui = FrontEndBase.createfrontend("Play")
        self._inited = False
        self._empty = True
        self._warmup = 0
        self._hits = []
        self._detecteddarts = 0
        self._setscore = 0
        self._totalscore = 0
        self._statestruct =  {"player1": {"d1": "-", "d2": "-", "d3": "-", "set": "-" , "total": "-", "diff": "-", "done": False}}
        self._dartevallocked = False
        #TODO: load saved game
        #TODO: internal states MVP, one player:  startset -> d1 -> d2 -> d3 -> endset
        #TODO: extend states for 2 players and real game

    def update(self, frame, context):
        #TODO: move to calibrate state
        if self._warmup < dartconfig["play"]["warmupframes"]:
            self._warmup = self._warmup + 1
            return frame

        # TODO: complete refactory of this state-machine. Its very messy...
        if not self._inited:
            self._dartDetector = DartDetector.DartDetector(frame)
            self._previousFrame = frame.copy()
            self._previousboardstate = frame.copy()
            self._inited = True
           # print ("First frame (empty board) initialized in PlayState Loop..")
        else:
            if self._dartDetector.boardEmpty(frame):
                self._hits = []
                self._detecteddarts = 0
                self._setscore = 0
                # Reset statestruct
                self._statestruct["player1"]["d1"] = 0
                self._statestruct["player1"]["d2"] = 0
                self._statestruct["player1"]["d3"] = 0
                self._empty = True
                self._dartDetectorFrames = 0
                self._dartDetector._lastscore = None
            else:
                #print("Detected not empty")
                self._empty = False
                if self._dartDetector.boardChanged(frame, self._previousFrame):
                    if self._dartevallocked:
                        self._dartevallocked = False
                else:  #Not changed, board stabilized
                    if  self._dartDetectorFrames < dartconfig["DartHit"]["DartHitFrames"]:
                        self._dartDetectorFrames =  self._dartDetectorFrames +1
                    else:
                        if not self._dartevallocked:
                            if self._dartDetector.detectDart(frame, self._previousboardstate):
                                score = self._dartDetector._lastscore
                                self._detecteddarts = self._detecteddarts + 1
                                # TODO: Uodate state-structure here...
                                self._setscore = self._setscore + score
                                d = "d" + str(self._detecteddarts)
                                self._totalscore = self._totalscore + score
                                self._statestruct["player1"][d] = str(score)
                                self._statestruct["player1"]["total"] = self._totalscore
                                self._previousboardstate = frame.copy() #board stabilized, make new boardstate
                                self._dartevallocked = True   #Lock evaluation until board change again
            self._previousFrame = frame.copy()
            self._statestruct["player1"]["total"] = self._totalscore
        self._gui.update(self._statestruct)
        return frame


    def draw(self, frame):
        if self._inited:
            if self._empty:
                cv2.putText(frame,"Board empty", (5,50),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
            else:
                cv2.putText(frame,"Board not empty", (5,50),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
                frame = self._dartDetector.draw(frame)
            cv2.putText(frame,"Play State", (5,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        else:
            cv2.putText(frame,"Play State - warming up", (5,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        if self._dartevallocked:
            cv2.putText(frame,"Dart evaluation locked", (5,80),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        else:
            cv2.putText(frame, "Dart evaluation not locked", (5, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        self._gui.draw(frame)
        return frame



if __name__ == "__main__":
    import Cam
    import numpy as np
    import pygame
    pygame.init()
    from DartScoreEngine.Utils import testutils

    psl = PlayStateLoop()
    psl.initialize()


    cap = Cam.createCam("STREAM")
    cap.initialize('http://192.168.1.131:8081')
    transform = np.float32([[1.78852294e+00, -1.10143263e-01, -4.85063747e+02],
                            [2.17855239e-01, 1.03682933e+00, -3.82665632e+01],
                            [1.28478485e-03, -1.58506840e-04, 1.00000000e+00]])

    cap.settransformmatrix(transform)
    stopped = False
    while not stopped:  # Capture frame-by-frame
        frame = cap.update()
        psl.update(frame)
        psl.draw(frame)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                stopped = True

    pygame.quit()