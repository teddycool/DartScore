__author__ = 'teddycool'

import cv2
import time

class VideoPresenter(object):

    def __init__(self):
        self._windowname = "VideoPresenter"


    def draw(self, frame):
        cv2.imshow(self._windowname, frame)


    def __del__(self):
        cv2.destroyAllWindows()


if __name__ == '__main__':
    print "Testcode for videpresenter"
    print cv2.__version__
    cam = cv2.VideoCapture("C:/Users/psk/Documents/GitHub/DartScore/Testdata/Videos/dartscoreRaw_20170327_193108.avi")
    pres = VideoPresenter()

    while True:
        ret, frame = cam.read()
        pres.draw(frame)
        time.sleep(0.5)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()
