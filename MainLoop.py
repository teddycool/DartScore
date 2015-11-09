__author__ = 'teddycool'
#State-switching and handling of general rendering
#from Inputs import Inputs
#from Board import Board
from Vision import Vision
import time
from  StateLoops import CamCalibrateLoop, CamMoutningLoop, PlayStateLoop

class MainLoop(object):
    def __init__(self):
        #self._inputs=Inputs.Inputs(self)
        #self._board = Board.Board()
        self._vision= Vision.Vision()
        self._calibrateState = CamCalibrateLoop.CamCalibrateLoop()
        self._mountingState = CamMoutningLoop.CamMountingLoop()
        self._playState = PlayStateLoop.PlayStateLoop()
        self._state = {"MountState": self._mountingState, "CalState": self._calibrateState, "PlayState": self._playState}
        #Start -> MountState ->[button]-> CalState ->[auto when done]-> PlayState ---> End...
        self._currentStateLoop = self._state["PlayState"]

    def initialize(self):
        print "Main init..."
        #self._inputs.initialize()
        self.time=time.time()
        self._vision.initialize()
        #Init all states
        for key in self._state.keys():
            self._state[key].initialize()
        print "Game started at ", self.time

    def update(self):
        frame = self._vision.update()
        self._currentStateLoop.update(frame)
        return frame

    def draw(self, frame):
        frame = self._currentStateLoop.draw(frame)
        self._vision.draw(frame) #Actually draw frame to mjpeg streamer...


    def changeState(self, newstate):
        if (newstate == 0) or (newstate == "InitState"):
            self._currentStateLoop = CamCalibrateLoop.CamCalibrateLoop()

        self._currentStateLoop.initialize()
        return newstate