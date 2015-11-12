__author__ = 'teddycool'
#Ref: http://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/

import cv2

class DartDetector(object):

    def __init__(self, boardemptyframe):
        self._boundingRects = []
        self._rawCnts = []
        self._boardEmptyFrame = boardemptyframe.copy()

    def boardEmpty(self, frame):
        print "Board empty?"
        cnts = self._frameDeltaBoundingBoxes(self._boardEmptyFrame, frame)
        return len(cnts)== 0

    def boardChanged(self, frame1, frame2):
        print "Board changed?"
        cnts = self._frameDeltaBoundingBoxes(frame1, frame2)
        return len(cnts)> 0


    def detectDart(self, frame1, frame2):
        print "Dart detected?"
        self._boundingRects = self._frameDeltaBoundingBoxes(frame1, frame2)
        return len(self._boundingRects)> 0

    def draw(self, frame):
        print "Draw dart"
        #for (x, y, w, h) in self._rawCnts:
        #    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        for (x, y, w, h) in self._boundingRects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return frame

    def _prepareFrame(self,frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (11, 11), 0)
        return gray


    def _frameDeltaBoundingBoxes(self, frame1, frame2):
        boundingRects = []
        gray1 = self._prepareFrame(frame1)
        gray2 = self._prepareFrame(frame2)
        # compute the absolute difference between the frames
        frameDelta = cv2.absdiff(gray1,gray2)
        thresh = cv2.threshold(frameDelta, 20, 255, cv2.THRESH_BINARY)[1]
        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
         # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            #TODO: move minarea to dartconfig file
            print "Area = " + str( cv2.contourArea(c))
            if cv2.contourArea(c) > 500:
                rect = cv2.boundingRect(c)
                boundingRects.append(rect)
        print "Counts for contours bigger then x: " + str(len(boundingRects))
        print "Raw counts for contours that differs: " + str(len(cnts))
        self._rawCnts = cnts
        return boundingRects


if __name__ == '__main__':
    print "Testcode for DartFinder"
    frame1 = cv2.imread("seq10.jpg")
    frame2 = cv2.imread("seq34.jpg")
    frame3 = cv2.imread("seq20.jpg")
    frame4 = cv2.imread("seq66.jpg")
    dd = DartDetector(frame1)
    print dd.detectDart(frame1, frame2)  #True
    frame = dd.draw(frame2)  #False
    print dd.boardEmpty(frame3)#True
    print dd.boardChanged(frame1, frame3)
    cv2.imshow("Darts found...", frame)
    cv2.waitKey(0)
