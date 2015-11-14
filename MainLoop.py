__author__ = 'teddycool'
#State-switching and handling of general rendering
#from Inputs import Inputs
#from Board import Board
from Vision import Vision
import time
from  StateLoops import CamCalibrateLoop, CamMoutningLoop, PlayStateLoop
from Inputs import IoInputs
#Global GPIO used by all...
import RPi.GPIO as GPIO


class MainLoop(object):
    def __init__(self):
        #TODO: fix logging to file readable from web
        #self._inputs=Inputs.Inputs(self)
        #self._board = Board.Board()
        self._vision= Vision.Vision()
        self._calibrateState = CamCalibrateLoop.CamCalibrateLoop()
        self._mountingState = CamMoutningLoop.CamMountingLoop()
        self._playState = PlayStateLoop.PlayStateLoop()
        self._state = {"MountState": self._mountingState, "CalState": self._calibrateState, "PlayState": self._playState}
        #Start -> MountState ->[button]-> CalState ->[auto when done]-> PlayState ---> End...
        self._currentStateLoop = self._state["MountState"]
        self._calButton = IoInputs.PushButton(GPIO,23)
        self._gameButton = IoInputs.PushButton(GPIO,24)


    def initialize(self):
        print "Main init..."
        #self._inputs.initialize()
        self.time=time.time()
        self._vision.initialize()
        self._lastframetime = time.time()
        #Init all states
        for key in self._state.keys():
            self._state[key].initialize()
        self._calButton.initialize()
        print "Game started at ", self.time

    def update(self):
        frame = self._vision.update()
        self._currentStateLoop.update(frame)
        cal = self._calButton.update()
        #TODO: fix better state-machine, move to state-loops
        print "CalButton: " + cal
        if cal  == "Pressed":
            self.changeState("CalState") #Mounting ready
        if cal == "LongPressed":
            self.changeState("PlayState")  #Reset to playstate
        return frame

    def draw(self, frame):
        frame = self._currentStateLoop.draw(frame)
        self._calButton.draw(frame )
        framerate = 1/(time.time()-self._lastframetime)
        self._vision.draw(frame, framerate) #Actually draw frame to mjpeg streamer...
        self._lastframetime= time.time()


    def changeState(self, newstate):
        self._currentStateLoop = self._state[newstate]
        self._currentStateLoop.initialize()