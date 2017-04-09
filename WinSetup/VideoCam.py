__author__ = 'teddycool'

import cv2

class VideoCam(object):

    def __init__(self):
        print "VideoCam created"
        self._cam = cv2.VideoCapture("C:/Users/psk/Documents/darts/Darts/Darts_Testvideo_4.mp4")
        #self._cam = cv2.VideoCapture("C:/Users/psk/Documents/GitHub/DartScore/Testdata/Videos/dartscoreRaw_20170327_193108.avi")

    def initialize(self):
        return

    def update(self):
        (ret, frame) = self._cam.read()
        return frame

    def __del__(self):
        self._cam.release()




if __name__ == '__main__':
    print "Testcode for videocam"
    print cv2.__version__

    cam = VideoCam()

    frame = cam.update()

    cv2.imshow('simple',frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()