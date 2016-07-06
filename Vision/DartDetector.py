__author__ = 'teddycool'
#Purpose: detect when a dart hits the board and when the board is empty
#The bounding rect for the new dart is used by DartHit to figure out the coordinates for the hit
#Ref: http://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/

import cv2
from DartHit import DartHit
from DartScoreConfig import dartconfig

class DartDetector(object):

    def __init__(self, boardemptyframe):
        self._boundingRects = []
        self._rawCnts = []
        self._boardEmptyFrame = boardemptyframe.copy()
        self._darthit = DartHit()
        self._seqno =0

    def boardEmpty(self, frame):
        print "Board empty?"
        cnts = self._frameDeltaBoundingBoxes(self._boardEmptyFrame, frame)
        return len(cnts)== 0

    def boardChanged(self, frame1, frame2):
        print "Board changed?"
        cnts = self._frameDeltaBoundingBoxes(frame1, frame2)
        return len(cnts)> 0

    def detectDart(self, currentframe, previousframe):
        print "Dart detected?"
        self._boundingRects = self._frameDeltaBoundingBoxes(currentframe, previousframe)
        if len(self._boundingRects) > 0:
            rectno=0
            for rect in self._boundingRects:
                x,y,w,h = rect
                x1 = x+w
                y1 = y+h
                cropped = currentframe[y:y1, x:x1]
                self._darthit.initialize(cropped,rect)
                if dartconfig["DartHit"]["WriteFramesToSeparateFiles"]:
                    cv2.imwrite("dhframe"+str(self._seqno)+ "_" +str(rectno) +".jpg",cropped)
                    rectno = rectno +1
            self._seqno=self._seqno+1
        return len(self._boundingRects)> 0

    def draw(self, frame):
        print "Draw dart"
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
        (_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
         # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            #TODO: move minarea to dartconfig file
            print "Area = " + str( cv2.contourArea(c))
            if cv2.contourArea(c) > dartconfig["DartHit"]["DartHitMinArea"]:
                rect = cv2.boundingRect(c)
                boundingRects.append(rect)
        print "Counts for contours bigger then: " + str(len(boundingRects))
        print "Raw counts for contours that differs: " + str(len(cnts))
        self._rawCnts = cnts
        return boundingRects


if __name__ == '__main__':
    print "Testcode for DartFinder"
    frame1 = cv2.imread("camseq58.jpg")
    frame2 = cv2.imread("camseq64.jpg")
    frame3 = cv2.imread("camseq67.jpg")

    dd = DartDetector(frame1)
    print dd.detectDart(frame2, frame1)  #True
    frame = dd.draw(frame2)  #False
    print dd.boardEmpty(frame3)#True
    print dd.boardChanged(frame1, frame3)
    cv2.imshow("Darts found...", frame)
    x,y,w,h = dd._boundingRects[0]
    x1 = x+w
    y1 = y+h
    cropped = frame[y:y1, x:x1]
    cv2.imshow("DartPart",cropped )
    cv2.waitKey(0)
