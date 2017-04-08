__author__ = 'teddycool'
#New main for the complete game in a simple setup

import Cam
import Presenter
import cv2
import time


from DartScoreMainConfig import config



if __name__ == '__main__':
    print "Testcode for GameMain"
    env = config["Environment"]
    print "Starting for environment: " + env
    cam = Cam.createCam(env)
    pres = Presenter.createPresenter(env)
    cam.initialize()

    while True:
        frame = cam.update()
        if frame == None:
            break
        pres.draw(frame)
        time.sleep(0.1)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()