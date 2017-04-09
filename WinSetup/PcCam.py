__author__ = 'teddycool'
import cv2

class PcCam(object):

    def __int__(self):
        self._camId = 1


    def initialize(self):
        self._cam = cv2.VideoCapture(1)
       # self._cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1024)
       # self._cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 768)
        print str(self._cam.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
        print str(self._cam.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

    def update(self):
        (ret, frame) = self._cam.read()
        return frame

    def __del__(self):
        self._cam.release()

