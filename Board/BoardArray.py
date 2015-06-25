__author__ = 'teddycool'

import cv2
import numpy as np
import pygame
import math

# Class to create an array defining 'the perfect board' and a 'normalized' board used later on..


class BoardArray(object):

    def __init__(self, center=(250,250), radius = 225):
        self._lines = []
        self._circles = []
        self._center =center
        self._radius = radius

    def create(self, img):
        cv2.circle(img,self._center,225,(0,255,0),1) #outer
        cv2.circle(img,self._center,170,(0,255,0),1) #outside double
        cv2.circle(img,self._center,162,(0,255,0),1) #inside double
        cv2.circle(img,self._center,107,(0,255,0),1) #outside treble
        cv2.circle(img,self._center,99,(0,255,0),1) #inside treble
        cv2.circle(img,self._center,16,(0,255,0),1) #25
        cv2.circle(img,self._center,6,(0,255,0),1) #Bulls eye

        #20 sectors...
        sectorangle = 2*math.pi/20
        i=0
        while ( i<20):
            cv2.line(img,self._center, (int(self._center[0]+225*math.cos((0.5+i)*sectorangle)), int(self._center[1]+225*math.sin((0.5+i)*sectorangle))), (0,255,0), 1)
            i=i+1
        return img


    def getScore(self, hit):

        score = 0
        return score



if __name__ == "__main__":

    img = cv2.imread("boardarraybg.jpg")
    bf = BoardArray()
    img = bf.create(img)
    cv2.imshow('img',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()