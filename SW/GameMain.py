__author__ = 'teddycool'
#New main for the complete game in a simple setup

import Cam
import Presenter
import cv2
import time


from GameMainConfig import config
from DartScoreEngine import MainLoop

class GameMain(object):
    def __init__(self):
        return

    def initialize(self):
        print ("Initialize for GameMain")
        env = config["Environment"]
        pres = config["Presenter"]
        self._cam = Cam.createCam(env)
        self._pres = Presenter.createPresenter(pres)
        self._cam.initialize()
        self._emainloop = MainLoop.MainLoop(self._cam, self._pres)
        self._emainloop.initialize()


    def update(self):
        frame = self._emainloop.update()
        self._emainloop.draw(frame)




if __name__ == '__main__':
    print ("Testcode for GameMain")
    print ("Starting for environment: " + config["Environment"])

    game= GameMain()
    game.initialize()

    while True:
        game.update()
        time.sleep(0.1)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break