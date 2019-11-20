__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore

# Purpose of this file:
# Find elipses in a picture of a dart-board (the rings in perspective of the cam)
# Input: image of dartboard, output: array of elipses...


from cv2 import cv2
from DartScoreEngine import DartScoreEngineConfig
from DartScoreEngine.Utils import visionutils
from DartScoreEngine.Utils import ShapeDetector


class Elipses(object):

    def __init__(self):
        self._circles = []
        self._contours = []
        self._shapedetector = ShapeDetector.ShapeDetector()


    def findElipses(self,img):
        imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(imgray, 127, 255, 0)
        img, self._contours, self._hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


    # find the outer segments between 2x and 3x sectors.
    # apply two masks, one for dark and one for light areas, filter on size/area and number of corners
    def findouterslices(self, img):
        imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(imgray, 50, 180, 0)
        img, contours, self._hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if self._shapedetector.detect(cnt)not in ["circle", "triangle", "pentagon"]:
                if cv2.contourArea(cnt) > 2100 and cv2.contourArea(cnt) < 8000:
                    self._contours.append(cnt)
        return self._contours


if __name__ == "__main__":
    from DartScoreEngine.Utils import testutils

    cam = testutils.GetTestVideoCapture()
    (ret, frame) = cam.read()
    index = 0

    originalimg = frame.copy()
    contourimg = frame.copy()

    elipses = Elipses()

    sectorscontours = elipses.findouterslices(frame)



    cv2.drawContours(contourimg, sectorscontours, -1, (0, 255, 0), 3)



    cv2.imshow('orig', originalimg)
    cv2.imshow('Contours', contourimg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
