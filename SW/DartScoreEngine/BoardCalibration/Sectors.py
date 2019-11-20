__author__ = 'teddycool'
#Purpose: finding sector circles on dartboard image

from cv2 import cv2
import numpy as np


class Sector(object):

    def __init__(self):
        self._contours = []
        self._hierarchy = []
        return


    def initialize(self, img):
       return

    def _findSectorCircles(self, img):

        imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(imgray,100,255,0)
        img, self._contours, self._hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
       
        return self._contours




# Unit-test of this module
if __name__ == "__main__":
    from DartScoreEngine.Utils import testutils
    cam = testutils.GetTestVideoCapture()
    (ret, frame) = cam.read()
    index = 0

    originalimg = frame.copy()
    contourimg = frame.copy()

    sector = Sector()

    sectorscontours = sector._findSectorCircles(frame)

    cv2.drawContours(contourimg, sector._contours, -1, (0,255,0), 1)
    #print (sector._contours)

    cv2.imshow('orig',originalimg)

    cv2.imshow('Contours',contourimg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()