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
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        edged = cv2.Canny(blurred, 30, 150)
        (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        if len(cnts) > 0:
            self._cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[0:30]
        cv2.imshow("Frame", gray)
        cv2.imshow("Edged", edged)

    def draw(self, frame):
        print "Found contours: " + str(len(self._cnts))
        if len(self._cnts) >  0:
            frame = cv2.drawContours(frame, self._cnts, -1, (0, 0, 255), 2)
            #print "Contour drawn: " + str(self._cnts[1])
        return frame

if __name__ == '__main__':
    rhigh = (100, 100, 255)
    rlow = (30,30,150)
    ghigh = [100, 255, 100]
    glow = [30,80,40]
    bhigh = [35, 35, 45]
    blow = [5,5,5]
    print "Testcode for ContourFinder"
    frame = cv2.imread("camseq300.jpg")
    sf = SectorFinder(blow, bhigh)
    sf.initialize()
    sf.update(frame)

    sf.draw(frame)
    cv2.imshow("Contours sectors", frame)
    print sf._cnts
    cv2.waitKey(0)

