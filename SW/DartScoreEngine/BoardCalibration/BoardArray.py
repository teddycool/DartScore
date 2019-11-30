__author__ = 'teddycool'

import math

from cv2 import cv2

from DartScoreEngine import  DartScoreEngineConfig


# Class to create an array defining 'the perfect board' and a 'normalized' board used later on..
# Actual board is 450 mm in diameter,  1 pixel per mm


class BoardArray(object):

    def __init__(self, center=(250,250), radius = 225):
        self._lines = []
        self._circles = []
        self._center =center
        self._radius = radius

    def create(self, img):
        scolor = (0, 0, 255) #DartScoreEngineConfig.dartconfig['color']['sector']

        cv2.circle(img,self._center,225,scolor,1) #outer
        cv2.circle(img,self._center,170,scolor,2) #outside double
        cv2.circle(img,self._center,162,scolor,2) #inside double
        cv2.circle(img,self._center,107,scolor,2) #outside treble
        cv2.circle(img,self._center,99,scolor,2) #inside treble
        cv2.circle(img,self._center,16,scolor,2) #25
        cv2.circle(img,self._center,6,scolor,2) #Bulls eye

        #20 sectors...
        sectorangle = 2*math.pi/20
        i=0
        while ( i<20):
            cv2.line(img,self._center, (int(self._center[0]+170*math.cos((0.5+i)*sectorangle)), int(self._center[1]+170*math.sin((0.5+i)*sectorangle))), scolor, 2)
            i=i+1
        return img

    # Gets the coordinates for the transformationvector
    # Inparameter: the largest sector angle where 0 is sector for '6', 0.5 pi rad '20' etc...
    # Return 4 point to use as the correct aspect in the transform...
    def gettransformvector(self, lsector):
        pass

    # Get the scores for the pixel that was hit by the dart after transform...
    # polar coordinates?
    def getscore(self, hitpoint):
        pass



if __name__ == "__main__":
    

    img = cv2.imread("boardarraybg.jpg")
    bf = BoardArray()
    img = bf.create(img)
    cv2.imshow('img',img)
    cv2.imwrite("perfectboard.jpg",img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()