__author__ = 'teddycool'
#TODO: break up this to pieces..
import cv2
import numpy as np
import socket

import BoardArray
from DartScoreEngine import DartScoreEngineConfig


class Board(object):

    def __init__(self, width, heigth):
        self._ilines = []
        self._circles = []
        self.imageX, self.imageY = self.width, self.height = (width,heigth)
        self._bullseye=(0,0)
        self._scalibrate = DartScoreEngineConfig.dartconfig['color']['calibrate']
        self._centersectorlines = [] #lines that
        self._transformmatrix = None



    def initialize(self, img):
       #Run self calibration
       self.findSectorLines(img)
       self._ba=BoardArray.BoardArray(self._bullseye)
       return


    def update(self):
        return

    def draw(self, img):
        #Draw current board on screen
        for i in range(len(self._ilines)):
            cv2.line(img,self._bullseye,self._ilines[i][1],self._scalibrate,1)
        return img


    def _auto_canny(self, image, sigma=0.33):
        # compute the median of the single channel pixel intensities
        v = np.median(image)

        # apply automatic Canny edge detection using the computed median
        lower = int(max(0, (1.0 - sigma) * v))
        upper = int(min(255, (1.0 + sigma) * v))
        edged = cv2.Canny(image, lower, upper)
        #return the edged image
        return edged


    def _intersect(self, line1, line2):
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
           raise Exception('lines do not intersect')

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return x, y


    #Find all sectorlines on the actual board and calculate sectors
    #TODO: separate finding lines from drawing lines
    #TODO: find the 2 sectorlines with highest positive and negative 'k' (Enclosing center sectors)
    #TODO: Find corresponding X-coordinates for +/- 96 on Y (perfect board has a rectangle (96,-15),(-96,15)) use these for transform.
    #TODO: Try with several settings until enough lines have been found? (or timeout)
    def findSectorLines(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray.copy(), (3, 3), 0)
        edges = self._auto_canny(gray)
        #edges = cv2.Canny(img.copy(), 10, 200)
        lines = cv2.HoughLines(edges,1,np.pi/180,130)
        #print "Lines " + lines[0]

        #Each line is represented by a two-element vector  (rho, theta) .
        # rho is the distance from the coordinate origin  (0,0) (top-left corner of the image).
        # theta is the line rotation angle in radians ( 0 \sim \textrm{vertical line}, \pi/2 \sim \textrm{horizontal line} ).
        if lines != None:
            templines = []
            for rho,theta in lines[0]:
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(a))
                templines.append(((x1,y1),(x2,y2)))
            noLines =  len(templines)
            xpoint=[]
            ypoint =[]
            crosspoint = []

            for i in range(noLines):
                for j in range(noLines):
                    if i < j:
                        try:
                            offsetx = DartScoreEngineConfig.dartconfig['mounting']['aimrectx'] / 2
                            offsety = DartScoreEngineConfig.dartconfig['mounting']['aimrecty'] / 2
                            cross =self._intersect(templines[i],templines[j])
                            if cross[0] < self.imageX/2+offsetx and cross[0] > self.imageX/2 -offsety:
                                if cross[1] < self.imageY/2+offsety and cross[1] > self.imageY/2 - offsety :
                                    self._ilines.append(templines[i])
                                    #cv2.line(img,self._lines[i][0],self._lines[i][1],self._scalibrate,1)
                                    crosspoint.append(cross)
                                    xpoint.append(cross[0])
                                    ypoint.append(cross[1])
                        except:
                            pass
            try:
                self._bullseye = (int(np.median(xpoint)),int(np.median(ypoint)))
                print "Bullseye: ", self._bullseye
            except:
                print "Camera has to face a dartboard!"




    def _findSectorLines(self, img):
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50,150,apertureSize = 3)
        minLineLength = 150
        maxLineGap = 15
        lines = cv2.HoughLinesP(edges,1,np.pi/180,150,None,minLineLength,maxLineGap)
        for x1,y1,x2,y2 in lines[0]:
            cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
        return img


    def calculateLines(self):
        maxposk = 0
        maxnegk = 0
        maxposline = None
        maxnegline = None
        for line in self._ilines:
            k = (line[1][1]-line[0][1])/(line[1][0]-line[0][0])
            if k > maxposk:
                maxposk = k
                maxposline = line
            if k < maxnegk:
                maxnegk = k
                maxnegline = line
        return [maxposline, maxnegline]





if __name__ == "__main__":
    #cam= cv2.VideoCapture("C:/Users/psk/Documents/darts/Darts/Darts_Testvideo_4.mp4")
    cam = cv2.VideoCapture("C:/Users/psk/Documents/GitHub/DartScore/Testdata/Videos/dartscoreRaw_20170327_193108.avi")
    (ret, frame) = cam.read()

    width =  cam.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    heigth = cam.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)


    bf = Board(width,heigth)
    original=frame.copy()
    sectors = frame.copy()
    maxmin = frame.copy()

    bf.initialize(frame)
    sectors = bf.draw(sectors)
    ba=BoardArray.BoardArray(bf._bullseye)
    ba.create(frame)

    #maxminlines = bf.calculateLines()
# for line in maxminlines:
 #       cv2.line(maxmin,line[0],line[1],bf._scalibrate,1)
    rect1 = (bf._bullseye[0]-15, bf._bullseye[1]+96)
    rect2 = (bf._bullseye[0]+15, bf._bullseye[1]-96)

    cv2.imshow('orig',original)
    cv2.imshow('Step 1 Bulls eye',frame)
    cv2.rectangle(maxmin, rect1, rect2, DartScoreEngineConfig.dartconfig['color']['aim'], 2)
    cv2.imshow('Step 2 before transform',sectors)
    cv2.imshow('Step 3 before transform',maxmin)
    cv2.waitKey(0)
    cv2.destroyAllWindows()