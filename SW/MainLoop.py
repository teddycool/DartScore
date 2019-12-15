__author__ = 'teddycool'

# DartScore MainLoop
# State-switching and handling of general rendering
# -> update -> draw....



import time
import sys
import numpy as np
import os

sys.path.append("/home/pi/DartScore/SW")

from DartScoreEngine.DartScoreEngineConfig import dartconfig
from  DartScoreEngine.StateLoops import PlayStateLoop
from DartScoreEngine.StateLoops import CamCalibrateLoop
from DartScoreEngine.StateLoops import CamMoutningLoop
from DartScoreEngine.Vision import Vision
import Cam
from FrontEnd import GameFrontEnd



class MainLoop(object):
    def __init__(self, camurl = dartconfig["cam"]["camurl"]):
        #TODO: fix logging to file readable from web
        self._cam = Cam.createCam("STREAM")
        self._cam.initialize(camurl)
        self._calibrateState = CamCalibrateLoop.CamCalibrateLoop()
        self._mountingState = CamMoutningLoop.CamMountingLoop()
        self._playState = PlayStateLoop.PlayStateLoop()
        self._state = {"PlayState": self._playState, "CalState": self._calibrateState, "MountingState": self._mountingState}

        if os.path.isfile(dartconfig["calibration"]["savepath"]):  #Calfile exists, presuming board and cam allready in place
            self._currentStateLoop = self._state["CalState"]
        else:
            self._currentStateLoop = self._state["MountingState"]

        self._tmatrix = None
        #TODO: add an IO for red and green button...

    def initialize(self):
        print ("Main init...")
        print (r"DartScore:  Copyright (C) 2019  Pär Sundbäck, mailto:par@sundback.com   http://www.github.com/teddycool")
        print ("This program comes with ABSOLUTELY NO WARRANTY")
        print ("This is free software, and you are welcome to redistribute it under certain conditions")
        print ("DartScore is licensed under GPL3. Full description in license.md in the root directory")

        time.sleep(2)

        self.time=time.time()
        self._lastframetime = time.time()
        # Init all states
        for key in self._state.keys():
            self._state[key].initialize()
        #print ("Game started at ", self.time)

    def update(self):
        start = time.time()
        frame = self._cam.update()
        self._currentStateLoop.update(frame, self)
        #print ("Main update time: " + str(time.time()-start))
        #TODO: if green button pressed -> next state
        #TODO: if red button longpressed -> shut down...
        return frame

    def draw(self, frame):
        start = time.time()
        frame = self._currentStateLoop.draw(frame)

      #  framerate = round(1/(time.time()-self._lastframetime),2)
      #  self._lastframetime= time.time()
     #   self._vision.draw(frame, framerate) #Actually draw frame to mjpeg streamer...
       # self._gui.draw(frame)
        #print ("Main draw time: " + str(time.time()-start))


    def changeState(self, newstate):
        self._currentStateLoop = self._state[newstate]
        self._currentStateLoop.initialize()



