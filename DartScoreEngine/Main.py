__author__ = 'teddycool'
# Main for the DartScore engine statemachine
# Takes a cam and a presenter device as arguments
# Publish data to a ??
# When the game is played this will run in the background

import os
import sys
sys.path.append(r'C:\Users\par\OneDrive\Documents\GitHub\DartScore')

import time

from DartScoreEngine import MainLoop


class Main(object):

    def __init__(self, cam, presenter):
        print ("Init Main object...")
        self._mainLoop=MainLoop.MainLoop(cam, presenter)


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
    
    import Cam 
    from FrontEnd import FrontEnd
    cam = Cam.createCam("STREAM")
    frontend = FrontEnd.FrontEnd(1024,768)
    gl=Main(cam, frontend)
    gl.run()
