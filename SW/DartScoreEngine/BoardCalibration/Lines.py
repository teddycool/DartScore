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


    def findSectorLines(self, img):
        src = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        dst = cv2.Canny(src, 127, 255, None, 3)
        linesP = cv2.HoughLinesP(dst, 1, np.pi / 180, 50, None, 50, 10)

        return linesP


    def findBullsEye(self, lines):
        noLines = len(lines)
        xpoint = []
        ypoint = []
        crosspoint = []
        print(lines[0])

        for i in range(noLines):
            for j in range(noLines):
                if i < j:
                    try:
                        linestri = lineutils.stretchlines(lines[i])
                        linestrj = lineutils.stretchlines(lines[j])
                        cross = lineutils.intersect(linestri, linestrj)
                        self._ilines.append(linestri)
                        crosspoint.append(cross)
                        xpoint.append(cross[0])
                        ypoint.append(cross[1])
                        print("Crossing: " + str(cross))
                    except:
                        pass

        try:
            print(crosspoint)
            self._bullseye = (int(np.median(xpoint)), int(np.median(ypoint)))
            print("Bullseye: ", self._bullseye)
        except:
            print("Camera has to face a dartboard!")




if __name__ == "__main__":
    from DartScoreEngine.Utils import testutils
    cap = testutils.GetTestVideoCapture()
    (ret, frame) = cap.read()
    index = 0
    lines = Lines()
    print ("Frame # " + str(index) + " was captured")

    linesP = lines.findSectorLines(frame)

    dst = np.copy(frame)

    lines.findBullsEye(linesP)

    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            cv2.line(dst, (l[0], l[1]), (l[2], l[3]), (0, 255, 0), 1, cv2.LINE_AA)


    cv2.imshow("Source", frame)
    cv2.imshow('Lines',dst)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


    
    cap.release()
