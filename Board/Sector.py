__author__ = 'teddycool'
#Purpose: finding sector circles on dartboard image

import cv2
import numpy as np
import BoardArray
import DartScoreConfig

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
        self._contours, self._hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)





if __name__ == "__main__":

    snapshot = cv2.imread("C:\Users\psk\Documents\GitHub\DartScore\Vision\camseq300.jpg")

    originalimg=snapshot.copy()
    contourimg = snapshot.copy()

    sector = Sector()

    sectorscontours = sector._findSectorCircles(snapshot)

    cv2.drawContours(contourimg, sector._contours, -1, (0,255,0), 1)
    print sector._contours

    cv2.imshow('orig',originalimg)

    cv2.imshow('Contours',contourimg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()