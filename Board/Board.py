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
        self._scalibrate = DartScoreConfig.config['color']['calibrate']


    def initialize(self, img):
       #Run self calibration
       self._findSectorLines(img)
       self._ba=BoardArray.BoardArray(self._bullseye)
       return


    def update(self):
        return

    def draw(self, screen):
        #Draw current board on screen
        return screen


    def _auto_canny(image, sigma=0.33):
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
    def _findSectorLines(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray.copy(), (3, 3), 0)
        #edges = self._auto_canny(gray)
        edges = cv2.Canny(img.copy(), 10, 200)
        lines = cv2.HoughLines(edges,1,np.pi/180,130)
        print lines[0]
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
        print pLines[0]
        noLines=len(pLines)
        iLines = []
        xpoint=[]
        ypoint =[]
        crosspoint = []
        for i in range(noLines):
            for j in range(noLines):
                if i != j:
                    try:
                        offsetx = DartScoreConfig.config['mounting']['aimrectx']/2
                        offsety = DartScoreConfig.config['mounting']['aimrecty']/2
                        cross =self._intersect(pLines[i],pLines[j])
                        if cross[0] < self.imageX/2+offsetx and cross[0] > self.imageX/2 -offsety:
                            if cross[1] < self.imageY/2+offsety and cross[1] > self.imageY/2 - offsety :
                                iLines.append(pLines[i])
                                cv2.line(img,pLines[i][0],pLines[i][1],self._scalibrate,1)
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
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        #edges = self._auto_canny(blurred)
        edges = cv2.Canny(blurred, 150, 230)
        contours,h = cv2.findContours(edges,1,2)

        for cnt in contours:
            approx = cv2.approxPolyDP(cnt,0.1*cv2.arcLength(cnt,True),True)
            if len(approx) > 4:
                cv2.drawContours(img,[cnt],0,self._scalibrate,1)

        return img


    def _findSectors(self, lines, circles): 
        sectors = []
        #----
        return sectors

if __name__ == "__main__":

    snapshot = cv2.imread("C:\Users\psk\Documents\GitHub\DartScore\Board\seq15.jpg")

    bf = Board()
    bf.initialize()
    original=snapshot.copy()
    snapshot = bf._findSectorLines(snapshot)
    cv2.imshow('sectorlines',snapshot)
    snapshot = bf._findCircleLines(snapshot)
    ba=BoardArray.BoardArray(bf._bullseye)
    cv2.imshow('sector and circle lines',snapshot)
    ba.create(snapshot)
    cv2.imshow('orig',original)
    cv2.imshow('sector, circle lines and boardarray',snapshot)
    cv2.waitKey(0)
    cv2.destroyAllWindows()