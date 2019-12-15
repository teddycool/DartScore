__author__ = 'teddycool'

import math

from cv2 import cv2
import numpy as np

from DartScoreEngine import  DartScoreEngineConfig


# Class to create an array defining 'the perfect board' and a 'normalized' board used later on..
# Actual board is 450 mm in diameter,  1 pixel per mm


class BoardArray(object):

    def __init__(self, center=(250,250), radius = 225):
        self._lines = []
        self._circles = []
        self._center =center
        self._radius = radius

        sector = 2*math.pi/20

        self._pointsectors = [[0.5*sector,6], [1.5*sector,13], [2.5*sector, 4], [3.5*sector,18],
                              [4.5*sector,1],[5.5*sector, 20], [6.5*sector,5], [7.5*sector, 12],
                              [8.5*sector, 9],[9.5*sector, 14],[10.5*sector, 11],[11.5*sector, 8],
                              [12.5*sector, 16], [13.5*sector, 7], [14.5*sector, 19], [15.5*sector, 3],
                              [16.5*sector, 17], [17.5*sector, 2], [18.5*sector, 15],[19.5*sector, 10],
                              [20*sector, 6]]

    def draw(self, img):
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

    # Get the scores for the pixel that was hit by the dart after transform...
    # Calculate polar coordinates and then the scores..
    def getscore(self, hitpoint):           # hitpoint is a tuple (x,y)
        x = hitpoint[0] - self._center[0]
        y = hitpoint[1] - self._center[1]
        print("--------------")
        print("Values from getscore:")
        print  (hitpoint, x, y)

        #Calculate length
        r =  math.sqrt(x*x + y*y)
        a = None
        scorebase = None

        #Calculate angle
        if x == 0:
            if y > 0:
                a = math.pi/2
            if y < 0:
                a = math.pi*1.5
            if y == 0:
                a = 0
        if y == 0:
            if x > 0:
                a = 0
            if x < 0:
                a = math.pi

        if x > 0 and y < 0:  #Top right quarter
            a = math.atan(x/y) + 0.5*math.pi

        if x < 0 and y < 0: #Top left quarter
            a=  math.atan(x/y) + 0.5* math.pi

        if x < 0 and y > 0:  #Low left quarter
            a = math.atan(x/y) + 1.5*math.pi

        if x > 0 and y > 0: #Low right quarter
            a = math.atan(x/y) + 1.5*math.pi

        #Calculate 'score base'
        for sector in self._pointsectors:
            if a < sector[0]:
                scorebase = sector[1]
                break

        # Calculate multiple or center hit

        if r < 6:                   #Bullseye
            score = 50
        elif r < 16:                #Center ring
            score = 25
        elif r > 99 and r < 107:    #Trippel ring
            score = 3* scorebase
        elif r > 162 and r < 170:   #Double ring
            score = 2*scorebase
        elif r <  170:              #Some where else on score area = 1*
            score = scorebase
        else:
            score = 0               #Outside the score area

        print("Score: " + str(score))
        print("--------------")
        return score




if __name__ == "__main__":
    

    img = cv2.imread("boardarraybg.jpg")
    bf = BoardArray()
    print(bf.getscore((250, 250)))
    print (bf.getscore([250,80]))
    print (bf.getscore([125,125]))
    print(bf.getscore([250, 410]))
    print(bf.getscore([250, 85]))
    print(bf.getscore((231, 163)))
    img = bf.draw(img)
    cv2.imshow('img',img)
    cv2.imwrite("perfectboard.jpg",img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()