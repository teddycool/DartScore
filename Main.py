__author__ = 'teddycool'

# Put up the camera, run calibrate
# Start to play...


import MainLoop
import time


class Main(object):

    def __init__(self):
        print "Init Main object..."
        self._mainLoop=MainLoop.MainLoop()


    def run(self):
        self._mainLoop.initialize()
        stopped = False
        running=True
        while not stopped:
            frame = self._mainLoop.update()
            self._mainLoop.draw(frame)
            time.sleep(0.2)


#Testcode to run module. Standard Python way of testing modules.
#OBS !! comment out   line 47: "C:\Python27\Lib\site-packages\pygame\_camera_vidcapture.py":
#       #self.dev.setresolution(width, height) on row 49 in:
#
if __name__ == "__main__":
    #Set to webcam ID, std is 0. Networkedcam is probably 1
    #camid=1
    #Set size of screen/window

    gl=Main()
    gl.run()
