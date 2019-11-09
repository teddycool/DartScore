__author__ = 'teddycool'

import cv2
import numpy as np

class SectorFinder(object):

    def __init__(self, lower=[100, 67, 0], upper=[255, 128, 50]):
        #Set values
        self._lower = np.array(lower, dtype = "uint8")
        self._upper = np.array(upper, dtype = "uint8")
        self._cnts= None
        return


    def initialize(self):

        return

    def update(self, frame):
        #Calculate sectors with current values first time
        self._cnts= []
        inrange = cv2.inRange(frame, self._lower, self._upper)
        inrange = cv2.GaussianBlur(inrange, (3, 3), 0)
        cv2.imshow("Frame", frame)
        cv2.imshow("Inrange", inrange)
        cv2.waitKey(0)
        (cnts, _) = cv2.findContours(inrange.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        if len(cnts) > 0:
            self._cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[0:20]

    def draw(self, frame):
        print "Found contours: " + str(len(self._cnts))
        if len(self._cnts) >  0:
            frame = cv2.drawContours(frame, self._cnts[1], -1, (255, 255, 255), 1)
            print "Contour drawn: " + str(self._cnts[1])
        return frame

if __name__ == '__main__':
    print "Testcode for ContourFinder"

    rhigh = (110, 110, 255)
    rlow = (30,30,150)
    ghigh = [100, 255, 100]
    glow = [30,80,40]
    bhigh = [35, 35, 45]
    blow = [5,5,5]

    frame = cv2.imread("camseq300.jpg")
    sf = SectorFinder(rlow, rhigh)
    sf.initialize()
    frame = sf.update(frame)

    sf.draw(frame)
    cv2.imshow("Contours sectors", frame)
    print sf._cnts
    cv2.waitKey(0)

