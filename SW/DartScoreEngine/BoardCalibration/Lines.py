__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore

# Purpose of this file:
# Find lines in a picture of a dart-board and calculate the coordinates for the bullseye (the sector separators)
# Input: image of dartboard, output: array of lines and the coordinates for bullseye



from cv2 import cv2
import numpy as np
from DartScoreEngine.Utils import lineutils


class Lines(object):

    def __init__(self):
        self._ilines = []
        self._circles = []
        self._bullseye= (0,0)
        self._crosspoint = []


    def findSectorLines(self, img):
        src = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        dst = cv2.Canny(src, 75, 150, None, 3)
        linesP = cv2.HoughLinesP(dst, 1, np.pi / 180, 200, maxLineGap=250)
        #TODO: Filter out lines not passing the middle of the board

        return linesP


    def findBullsEye(self, lines):
        noLines = len(lines)
        print (noLines)
        xpoint = []
        ypoint = []

        for i in range(0, noLines):
            for j in range(0, noLines):
                if i < j:

                    line1= lines[i][0]
                    line2 = lines[j][0]

                    l1 = (line1[0], line1[1]), (line1[2], line1[3])
                    l2 = (line2[0], line2[1]), (line2[2], line2[3])
                    print(l1)
                    print(l2)
                    print("----------")
                    try:
                        cross = lineutils.intersect(l1, l2)
                        if cross[0] > 300 and cross[0] < 800:
                            if cross[1] > 300 and cross[1] < 500:
                                self._crosspoint.append(cross)
                                xpoint.append(cross[0])
                                ypoint.append(cross[1])
                                print("Crossing: " + str(cross))
                    except:
                        pass

        try:
            print(self._crosspoint)
            self._bullseye = (int(np.median(xpoint)), int(np.median(ypoint)))
            print("Bullseye: ", self._bullseye)
        except:
            print("Camera has to face a dartboard!")




if __name__ == "__main__":
    import Cam

    cam = Cam.createCam("STREAM")

    cam.initialize('http://192.168.1.131:8081')

    frame = cam.update()
    index = 0

    lines = Lines()
    print ("Frame # " + str(index) + " was captured")

    linesP = lines.findSectorLines(frame)
    print (linesP)

    dst = np.copy(frame)

    lines.findBullsEye(linesP)



    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            cv2.line(dst, (l[0], l[1]), (l[2], l[3]), (0, 255, 0), 1, cv2.LINE_AA)


    for cr in lines._crosspoint:
        cross = (int(cr[0]), int(cr[1]))
        cv2.circle(dst, cross, 3, (0, 250, 0), 2)

    cv2.circle(dst, lines._bullseye, 3, (0, 0, 255), 2)


    cv2.imshow("Source", frame)
    cv2.imshow('Lines',dst)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
