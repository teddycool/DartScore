__author__ = 'teddycool'
#Ref: http://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/

import cv2

class DartDetector(object):

    def __init__(self, boardemptyframe):
        self._boundingRects = []
        self._boardEmptyFrame = boardemptyframe

    def boardEmpty(self, frame):
        cnts = self._frameDeltaBoundingBoxes(self._boardEmptyFrame, frame)
        return len(cnts)== 0

    def boardChanged(self, frame1, frame2):
        cnts = self._frameDeltaBoundingBoxes(frame1, frame2)
        return len(cnts)> 0


    def detectDart(self, frame1, frame2):
        self._boundingRects = []
        cnts = self._frameDeltaBoundingBoxes(frame1, frame2)

        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            #TODO: move minarea to dartconfig file
            if cv2.contourArea(c) < 40:
                continue
            rect = cv2.boundingRect(c)
            self._boundingRects.append(rect)
        return len(cnts)> 0

    def draw(self, frame):
        for (x, y, w, h) in self._boundingRects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return frame

    def _prepareFrame(self,frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        return gray


    def _frameDeltaBoundingBoxes(self, frame1, frame2):
        gray1 = self._prepareFrame(frame1)
        gray2 = self._prepareFrame(frame2)
        # compute the absolute difference between the frames
        frameDelta = cv2.absdiff(gray1,gray2)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        return cnts


if __name__ == '__main__':
    print "Testcode for DartFinder"
    frame1 = cv2.imread("seq10.jpg")
    frame2 = cv2.imread("seq34.jpg")
    frame3 = cv2.imread("seq20.jpg")
    frame4 = cv2.imread("seq66.jpg")
    dd = DartDetector(frame1)
    print dd.detectDart(frame1, frame2)
    frame = dd.draw(frame2)
    print dd.boardEmpty(frame3)
    print dd.boardChanged(frame1, frame3)
    cv2.imshow("Darts found...", frame)
    cv2.waitKey(0)
