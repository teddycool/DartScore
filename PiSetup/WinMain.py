__author__ = 'teddycool'
#New main for the windows-spart of the game in a simple setup

import time
import cv2

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

if __name__ == '__main__':
    print "Testcode for videpresenter"
    from VideoCam import VideoCam
    from VideoPresenter import VideoPresenter
    print cv2.__version__
    cam = VideoCam()
    pres = VideoPresenter()

    while True:
        frame = cam.update()
        pres.draw(frame)
        time.sleep(0.1)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
