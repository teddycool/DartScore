__author__ = 'psk'
import cv2
import numpy as np
import pygame

# Class for dartboard. Besides handling update/draw for board it also
# finds sectors in a picture of a dartboard and calibrate it.
#
# Allways calibrate board at start/init
# Tactics:
# 1 find crossing lines and save them in a list
# 2 Calculate centerpoint of board and save it
# 3 Find circlesegments and save them
# 4 Calculate missing lines
# 5 Calculate missing circle segments
# 6 Calculate and define each sector and its score, save as ??


class Board(object):

    def __init__(self):
        self._lines = []
        self._circles = []

    def initialize(self, imgsize):
        self.imageX = imgsize[0]
        self.imageY=imgsize[1]
        #Run self calibration


    def update(self):
        return

    def draw(self, screen):
        #Draw current board on screen
        return screen

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


    def _findSectorLines(self, img):
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray,100,200,apertureSize = 3)
        cv2.imshow('gray',gray)

        lines = cv2.HoughLines(gray,1,np.pi/180,200)
        pLines = []
        for rho,theta in lines[0]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            pLines.append(((x1,y1),(x2,y2)))

        noLines=len(pLines)
        iLines = []
        xpoint=[]
        for i in range(noLines):
            for j in range(noLines):
                if i != j:
                    try:
                        cross =self._intersect(pLines[i],pLines[j])
                        if cross[0] < self.imageX/2+0.20*self.imageX and cross[0] > self.imageX/2 -0.20*self.imageX :
                            if cross[1] < self.imageY/2+0.20*self.imageY and cross[1] > self.imageY/2 -0.20*self.imageY :
                                iLines.append(pLines[i])
                                cv2.line(img,pLines[i][0],pLines[i][1],(0,0,255),2)
                                xpoint.append(cross)
                    except:
                        pass
        print xpoint
        return img

    def _findCircleLines(self, img):
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        #img = cv2.medianBlur(img,5)
        #cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)

        circles = cv2.HoughCircles(gray,cv2.cv.CV_HOUGH_GRADIENT,1,150, param1=10,param2=15,minRadius=300,maxRadius=500)

        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            # draw the outer circle
            cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
            # draw the center of the circle
            cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)

        return img


    def _findSectors(self, lines, circles):
        sectors = []
        #----
        return sectors


if __name__ == "__main__":

    #snapshot = cv2.imread("images\\_K3_5730.png")
    snapshot = cv2.imread("images\\dartboard.jpg")
    bf = Board()
    bf.initialize((811,796))
    #bf=Board((640,480))
    img = bf._findSectorLines(snapshot)
    #img = bf._findCircleLines(snapshot)
    cv2.imshow('img',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()