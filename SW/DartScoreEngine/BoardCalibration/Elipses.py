__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore

# Purpose of this file:
# Find elipses in a picture of a dart-board (the rings in perspective of the cam)
# Input: image of dartboard, output: array of elipses...

# https://docs.opencv.org/3.4/da/d54/group__imgproc__transform.html
# https://pysource.com/2018/02/14/perspective-transformation-opencv-3-4-with-python-3-tutorial-13/

import sys

#sys.path.append("/home/pi/DartScore/SW")
#sys.path.append("/home/pi/Dartscore")

from cv2 import cv2
from DartScoreEngine import DartScoreEngineConfig
from DartScoreEngine.Utils import visionutils
from DartScoreEngine.Utils import ShapeDetector
import numpy as np


class Elipses(object):

    def __init__(self):
        self._circles = []
        self._contours = []
        self._shapedetector = ShapeDetector.ShapeDetector()
        self._smallestcnt = None
        self._largestcnt = None


    # find the outer segments between 2x and 3x sectors.
    # apply two masks, one for dark and one for light areas, filter on size/area and number of corners
    def findouterslices(self, img):
        imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(imgray, 55, 100, 0)
        img, contours, self._hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if self._shapedetector.detect(cnt)not in ["circle", "triangle", "pentagon"]:
                if cv2.contourArea(cnt) > 2100 and cv2.contourArea(cnt) < 8000:
                    self._contours.append(cnt)
        self._smallestcnt = self._contours[0]
        self._largestcnt =  self._contours[0]

        for cnt in self._contours:
            if cv2.contourArea(cnt) >  cv2.contourArea(self._largestcnt):
                self._largestcnt = cnt
            if cv2.contourArea(cnt) <  cv2.contourArea(self._smallestcnt):
                self._smallestcnt = cnt

        return [self._smallestcnt, self._largestcnt]



if __name__ == "__main__":
    from DartScoreEngine.Utils import testutils
    import Cam

    cam = Cam.createCam("STREAM")

    cam.initialize('http://192.168.1.131:8081')

    elipses = Elipses()
    frameindex = 0

    while (True):
        frame = cam.update()

        sectorscontours = elipses.findouterslices(frame)

        for cnt in sectorscontours:
            # x, y, w, h = cv2.boundingRect(cnt)
            # aspect_ratio = float(w) / h
            # print("Area of contour:" + str(cv2.contourArea(cnt)))
            # print("Aspect ratio: " + str(aspect_ratio))
            # leftmost = tuple(cnt[cnt[:, :, 0].argmin()][0])
            # rightmost = tuple(cnt[cnt[:, :, 0].argmax()][0])
            # topmost = tuple(cnt[cnt[:, :, 1].argmin()][0])
            # bottommost = tuple(cnt[cnt[:, :, 1].argmax()][0])
            # print("Leftmost: " + str(leftmost))
            # print("Rightmost: " + str(rightmost))
            # print("Topmost: " + str(topmost))
            # print("Bottommost: " + str(bottommost))
            # print ("---------------------")
            cv2.drawContours(frame, cnt, -1, (0, 250, 0), 3)

        correct = np.float32([[92,275], [392,178],[108,322], [408,225] ])

        skewed = np.float32([[276,337], [606,227],[293,392], [628,301] ])

        matrix = cv2.getPerspectiveTransform(skewed, correct)
        print(matrix)


        #
        result = cv2.warpPerspective(frame, matrix, (500, 500))
        cv2.putText(result, "Frame index " + str(frameindex), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        frameindex = frameindex + 1
        cv2.imshow('Warped1', result)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break