__author__ = 'teddycool'
import cv2
import numpy as np
import BoardArray
import DartScoreConfig

class Board(object):

    def __init__(self):
        self._lines = []
        self._circles = []
        self.imageX, self.imageY = self.width, self.height= DartScoreConfig.config['cam']['res']
        self._bullseye=(0,0)


    def initialize(self):
       #Run self calibration
        return


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
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(gray, 50, 200)

        lines = cv2.HoughLines(edges,1,np.pi/180,130)
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
        ypoint =[]
        crosspoint = []
        for i in range(noLines):
            for j in range(noLines):
                if i != j:
                    try:
                        cross =self._intersect(pLines[i],pLines[j])
                        if cross[0] < self.imageX/2+0.20*self.imageX and cross[0] > self.imageX/2 -0.20*self.imageX :
                            if cross[1] < self.imageY/2+0.20*self.imageY and cross[1] > self.imageY/2 -0.20*self.imageY :
                                iLines.append(pLines[i])
                                cv2.line(img,pLines[i][0],pLines[i][1],(0,0,255),2)
                                crosspoint.append(cross)
                                xpoint.append(cross[0])
                                ypoint.append(cross[1])
                    except:
                        pass

        self._bullseye = (int(np.median(xpoint)),int(np.median(ypoint)))
        print crosspoint
        print "Bullseye: ", self._bullseye
        return img

    def _findCircleLines(self, img):
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(gray, 50, 200)
        contours,h = cv2.findContours(edges,1,2)

        for cnt in contours:
            approx = cv2.approxPolyDP(cnt,0.1*cv2.arcLength(cnt,True),True)
            if len(approx) > 5:
                cv2.drawContours(img,[cnt],0,(0,0,255),2)
        return img


    def _findSectors(self, lines, circles):
        sectors = []
        #----
        return sectors

if __name__ == "__main__":
    import pygame
    from Cam import Cam
    cam=Cam.Cam()
    cam.initialize()
    t=0
    while t < 100:
        snapshot = cam.update()
        t= t+1
    print type(snapshot)
    snapshot = pygame.transform.rotate(snapshot,90)
    snapshot = pygame.transform.flip(snapshot, 0, 1)

    snapshot=pygame.surfarray.array3d(snapshot)
    print type(snapshot)
    #snapshot = cv2.imdecode(snapshot,0)
    print type(snapshot)


    bf = Board()
    bf.initialize()
    snapshot = bf._findSectorLines(snapshot)
    snapshot = bf._findCircleLines(snapshot)
    ba=BoardArray.BoardArray(bf._bullseye)
    ba.create(snapshot)
    cv2.imshow('img',snapshot)
    cv2.waitKey(0)
    cv2.destroyAllWindows()