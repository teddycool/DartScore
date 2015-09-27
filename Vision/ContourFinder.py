__author__ = 'teddycool'

import cv2
import numpy as np

class ContourFinder(object):

    def __init__(self):
        return


    def initialize(self):
        return

    def update(self, frame):
        self._cnts= []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 30, 150)
        (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts > 0:
            for cnt in cnts:
                ((x, y), radius) = cv2.minEnclosingCircle(cnt)
                if radius > 30 and radius < 100:
                    self._cnts.append(cnt)


    def draw(self, frame):
        if self._cnts >  0:
            cv2.drawContours(frame, self._cnts, -1, (0, 255, 0), 2)
        return frame

if __name__ == '__main__':
    print "Testcode for ContourFinder"
    frame = cv2.imread("pic1.jpg")
    cf = ContourFinder()
    frame = cf.update(frame)
    cf.draw(frame)
    cv2.imshow("Contours", frame)
    cv2.waitKey(0)
