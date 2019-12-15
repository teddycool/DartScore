__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore

# Purpose of this file:
# Find elipses in a picture of a dart-board (the rings in perspective of the cam)
# Input: image of dartboard, output: array of elipses...

# https://docs.opencv.org/3.4/da/d54/group__imgproc__transform.html
# https://pysource.com/2018/02/14/perspective-transformation-opencv-3-4-with-python-3-tutorial-13/

import sys
sys.path.append("/home/pi/DartScore/SW")

from cv2 import cv2
from DartScoreEngine.Utils import ShapeDetector
import numpy as np


class Sectors(object):

    def __init__(self):
        self._circles = []
        self._contours = []
        self._shapedetector = ShapeDetector.ShapeDetector()
        self._smallestcnt = None
        self._largestcnt = None


    # find the outer segments between 2x and 3x sectors.
    #TODO: parameterize the filter and tresh values
    def findouterslices(self, img, all= False):
        imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(imgray, 55, 100, 0)
        img, contours, self._hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if self._shapedetector.detect(cnt)not in ["circle", "triangle", "pentagon"]:
                if cv2.contourArea(cnt) > 2100 and cv2.contourArea(cnt) < 8000:
                    self._contours.append(cnt)

        for cnt in self._contours:
                left, right, top, bottom = self.findcorners(cnt)



        if all:
            return self._contours

        self._smallestcnt = self._contours[0]
        self._largestcnt =  self._contours[0]
        for cnt in self._contours:
            if cv2.contourArea(cnt) >  cv2.contourArea(self._largestcnt):
                self._largestcnt = cnt
            if cv2.contourArea(cnt) <  cv2.contourArea(self._smallestcnt):
                self._smallestcnt = cnt

        return self._smallestcnt, self._largestcnt


    def findcalcorners(self, contours, bullsey):
        # There should be 10 found sectors!
        if len(contours)!=10:
            return None

        # arrays to store the corners of the found sectors
        calcornertopright = []
        calcornerbottomright = []
        calcornertopleft = []
        calcornerbottomleft = []

        # Select which part of board each cnt belongs to and put the outer corner in correct array
        for cnt in contours:
            left, right, top, bottom = self.findcorners(cnt)
            if right[0]> bullsey[0]: #Right side of board
                if bottom[1] < bullsey[1]: # Top right
                    calcornertopright.append(right)
                if bottom[1] >  bullsey[1]:
                    calcornerbottomright.append(right)
            if right[0]< bullsey[0]:  #Left side of board
                if bottom[1] < bullsey[1]: # Top left
                    calcornertopleft.append(left)
                if bottom[1] >  bullsey[1]:
                    calcornerbottomleft.append(left)
          #  cv2.drawContours(frame, cnt, -1, (255, 0, 0), 3)

        # sort the arrays to find the middle sector outer corners in each part of the board
        self._calpointtopright =      sorted(calcornertopright, key=lambda tup: tup[1])[1]
        self._calpointbottomright=    sorted(calcornerbottomright, key=lambda tup: tup[0])[1]
        self._calpointtoppleft =      sorted(calcornertopleft, key=lambda tup: tup[0])[1]
        self._calpointbottomleft =    sorted(calcornerbottomleft, key=lambda tup: tup[0])[1]
        return  [self._calpointtopright , self._calpointbottomright, self._calpointtoppleft, self._calpointbottomleft]


    # not used?
    def findcorners(self, cnt):
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w) / h
        leftmost = tuple(cnt[cnt[:, :, 0].argmin()][0])
        rightmost = tuple(cnt[cnt[:, :, 0].argmax()][0])
        topmost = tuple(cnt[cnt[:, :, 1].argmin()][0])
        bottommost = tuple(cnt[cnt[:, :, 1].argmax()][0])
        return leftmost, rightmost, topmost, bottommost



if __name__ == "__main__":
    import sys
    import pygame
    import time
    sys.path.append("/home/pi/DartScore/SW")
    from DartScoreEngine.Utils import testutils
    import Cam
    from FrontEnd import GameFrontEnd
    from DartScoreEngine.BoardCalibration import BoardArray

    width = 1024
    height = 768
    gl = GameFrontEnd.GameFrontEnd(width, height)

    cam = Cam.createCam("STREAM")

    cam.initialize('http://192.168.1.131:8081')

    ba = BoardArray.BoardArray()

    sectors = Sectors()
    frameindex = 0
    stopped = False

    frame = cam.update()
    contours = sectors.findouterslices(frame, True)

    frame = sectors.findcalcorners( contours, (516, 319) )
    correct = np.float32([[137, 137], [363, 137], [363, 363], [137, 363]])

    skewed = np.float32([sectors._calpointtoppleft, sectors._calpointtopright, sectors._calpointbottomright,
                         sectors._calpointbottomleft])

    matrix = cv2.getPerspectiveTransform(skewed, correct)
    print(matrix)

    while not stopped:
        frame = cam.update()

        result = cv2.warpPerspective(frame, matrix, (500, 500))

        result = ba.draw(result)

        gl.draw(result)
        for event in pygame.event.get():
            if pygame.event.event_name(event.type).count('Quit') > 0:
              stopped = True

    pygame.quit()