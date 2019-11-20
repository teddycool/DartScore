# REF: https://www.pyimagesearch.com/2016/02/08/opencv-shape-detection/

# import the necessary packages
from cv2 import cv2


class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, c):
        # initialize the shape name and approximate the contour
        shape = "unidentified"
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        # if the shape is a triangle, it will have 3 vertices
        if len(approx) == 3:
            shape = "triangle"

        # if the shape has 4 vertices, it is either a square or
        # a rectangle
        elif len(approx) == 4:
            # compute the bounding box of the contour and use the
            # bounding box to compute the aspect ratio
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w / float(h)

            # a square will have an aspect ratio that is approximately
            # equal to one, otherwise, the shape is a rectangle
            shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"

        # if the shape is a pentagon, it will have 5 vertices
        elif len(approx) == 5:
            shape = "pentagon"

        # otherwise, we assume the shape is a circle
        else:
            shape = "circle"

        # return the name of the shape
        return shape


if __name__ == "__main__":
    from DartScoreEngine.Utils import testutils

    cam = testutils.GetTestVideoCapture()
    (ret, frame) = cam.read()
    index = 0
    shapedetector = ShapeDetector()

    imgray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 200, 255, 0)
    img,sectorscontours, _hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    originalimg = frame.copy()
    contourimg = frame.copy()



    # print (sector._contours)
    for cnt in sectorscontours:
        if shapedetector.detect(cnt) == "circle":
            cv2.drawContours(contourimg, cnt, -1, (0, 255, 0), 2)

    cv2.imshow('orig', originalimg)
    cv2.imshow('Contours', contourimg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()