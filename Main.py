__author__ = 'teddycool'

# Put up the camera, run calibrate
# Start to play...


import MainLoop
import time
from DartScoreConfig import dartconfig


class Main(object):

    def __init__(self):
        print "Init Main object..."
        self._mainLoop=MainLoop.MainLoop()


    def run(self):
        self._mainLoop.initialize()
        stopped = False
        while not stopped:
            framestarttime = time.time()
            frame = self._mainLoop.update()
            self._mainLoop.draw(frame)
            #time.sleep(0.01)


#Testcode to run module. Standard Python way of testing modules.

if __name__ == "__main__":
    #Set to webcam ID, std is 0. Networkedcam is probably 1
    #camid=1
    #Set size of screen/window

    gl=Main()
    gl.run()
