__author__ = 'teddycool'

import cv2
import numpy as np

class ContourFinder(object):

    def __init__(self):
        #Set values
        self._cnts= []
        return


    def initialize(self):

        return

    def update(self, frame):
        #Calculate sectors with current values first time
        self._cnts= []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        edged = cv2.Canny(blurred, 30, 150)
        (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts > 0:
            for cnt in cnts:
                ((x, y), radius) = cv2.minEnclosingCircle(cnt)
                if radius > 50 and radius < 150:
                    self._cnts.append(cnt)


    def draw(self, frame):
        print "Found contours: " + str(len(self._cnts))
        if len(self._cnts) >  0:
            frame = cv2.drawContours(frame, self._cnts, -1, (255, 255, 255), 1)
            print self._cnts
        return frame

if __name__ == '__main__':
    color = "Black"
    high = (10, 10, 10)
    low = (0,0,0)
    print "Testcode for ContourFinder"
    frame = cv2.imread("camseq300.jpg")
    cf = ContourFinder()
    cf.update(frame)
    cf.draw(frame)
    cv2.imshow("Contours for " + color + " sectors", frame)
    print cf._cnts
    cv2.waitKey(0)

