__author__ = 'psk'

import cv2
import numpy as np
import pygame

# Class to creat an array defining 'the perfect board'


class BoardArray(object):

    def __init__(self):
        self._lines = []
        self._circles = []

    def create(self, img):

        cv2.circle(img,(250,250),225,(0,0,0),1) #outer
        cv2.circle(img,(250,250),170,(0,0,0),1) #outside double
        cv2.circle(img,(250,250),162,(0,0,0),1) #inside double
        cv2.circle(img,(250,250),107,(0,0,0),1) #outside treble
        cv2.circle(img,(250,250),99,(0,0,0),1) #inside treble
        cv2.circle(img,(250,250),16,(0,0,0),1) #25
        cv2.circle(img,(250,250),6,(0,0,0),1) #Bulls eye

        return img








if __name__ == "__main__":

    #img=cv2.imread("\\images\\dartboard.jpg")
    img = cv2.imread("boardarraybg.jpg")
    bf = BoardArray()
    img = bf.create(img)
    cv2.imshow('img',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()