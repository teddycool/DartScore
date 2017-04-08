__author__ = 'teddycool'
#State-switching and handling of general rendering
import time


from DartScoreEngineConfig import dartconfig
from  StateLoops import CamCalibrateLoop, CamMoutningLoop, PlayStateLoop
from Vision import Vision


class MainLoop(object):
    def __init__(self):
        #TODO: fix logging to file readable from web
        self._vision= Vision.Vision()
        self._calibrateState = CamCalibrateLoop.CamCalibrateLoop()
        self._mountingState = CamMoutningLoop.CamMountingLoop()
        self._playState = PlayStateLoop.PlayStateLoop()
        self._state = {"MountState": self._mountingState, "CalState": self._calibrateState, "PlayState": self._playState}
        #Start -> MountState ->[button]-> CalState ->[auto when done]-> PlayState ---> End...
        self._currentStateLoop = self._state["MountState"]

    def initialize(self):
        print "Main init..."
        #self._inputs.initialize()
        self.time=time.time()
        self._vision.initialize()
        self._lastframetime = time.time()
        # Init all states
        for key in self._state.keys():
            self._state[key].initialize()
        print "Game started at ", self.time

    def update(self):
        start = time.time()
        frame = self._vision.update()
        self._currentStateLoop.update(frame)
        #TODO: fix better state-machine, move to state-loops
        # if cal  == "Pressed":
        #     self.changeState("CalState") #Mounting ready
        # if cal == "LongPressed":
        #     self.changeState("MountState")  #Reset to playstate
        # if game == "Pressed":
        #     self.changeState("PlayState")  #Reset to playstate
        print "Main update time: " + str(time.time()-start)
        return frame

    def draw(self, frame):
        start = time.time()
        frame = self._currentStateLoop.draw(frame)
        # self._calButton.draw(frame,"Cal", 5,80)
        # self._gameButton.draw(frame,"Game", 5,100)

        framerate = round(1/(time.time()-self._lastframetime),2)
        self._lastframetime= time.time()
        self._vision.draw(frame, framerate) #Actually draw frame to mjpeg streamer...
        print "Main draw time: " + str(time.time()-start)


    def changeState(self, newstate):
        #TODO: Move to state.deactivate

        self._currentStateLoop = self._state[newstate]
        self._currentStateLoop.initialize()


    def __del__(self):
        self._onLed.activate(False)
        self._gpio.cleanup()