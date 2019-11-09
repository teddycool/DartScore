__author__ = 'teddycool'
#State-switching and handling of general rendering
import time


from DartScoreEngineConfig import dartconfig
from  StateLoops import CamCalibrateLoop, CamMoutningLoop, PlayStateLoop
from Vision import Vision


class MainLoop(object):
    def __init__(self,cam, presenter ):
        #TODO: fix logging to file readable from web
        self._cam = cam
        self._pres = presenter
        self._vision= Vision.Vision()
        self._calibrateState = CamCalibrateLoop.CamCalibrateLoop()
        self._mountingState = CamMoutningLoop.CamMountingLoop()
        self._playState = PlayStateLoop.PlayStateLoop()
        self._state = {"MountState": self._mountingState, "CalState": self._calibrateState, "PlayState": self._playState}
        #Start -> MountState ->[button]-> CalState ->[auto when done]-> PlayState ---> End...
        self._currentStateLoop = self._state["CalState"]

    def initialize(self):
        print ("Main init...")
        self.time=time.time()
        self._cam.initialize()
        self._vision.initialize()
        self._lastframetime = time.time()
        # Init all states
        for key in self._state.keys():
            self._state[key].initialize()
        print ("Game started at ", self.time)

    def update(self):
        start = time.time()
        frame = self._cam.update()
        frame = self._vision.update(frame)
        self._currentStateLoop.update(frame)
        print ("Main update time: " + str(time.time()-start))
        return frame

    def draw(self, frame):
        start = time.time()
        frame = self._currentStateLoop.draw(frame)

        framerate = round(1/(time.time()-self._lastframetime),2)
        self._lastframetime= time.time()
        self._vision.draw(frame, framerate) #Actually draw frame to mjpeg streamer...
        self._pres.draw(frame)
        print ("Main draw time: " + str(time.time()-start))


    def changeState(self, newstate):
        #TODO: Move to state.deactivate
        self._currentStateLoop = self._state[newstate]
        self._currentStateLoop.initialize()

