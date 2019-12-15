__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore
#
# Purpose of this file:
# Takes a bounding-box for a dart and calculate hitpoint and scores


from cv2 import cv2

from DartScoreEngine.DartScoreEngineConfig import dartconfig
from DartScoreEngine.BoardCalibration import BoardArray


class DartHit(object):

    def __init__(self):   #Create everything once and reuse the instance for better performance
        self._hitframe = None
        self._score = None
        self._hitcoords = None
        self._boardarray = BoardArray.BoardArray()


    def update(self,hitframe, cnts): #This is where the actual score calculation takes palce
        # First set values to default
        self._score = None
        self._hitcoords = None

        #Now calculate the hitcoords and the score for this dart
        self._hitframe = hitframe
       # img, contours, hierarchy = cv2.findContours(hitframe, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #Find contour point with max x value
        maxx = 0
        for c in cnts:
            print(cv2.contourArea(c))

            # determine the most extreme points along the contour
          #  extLeft = tuple(c[c[:, :, 0].argmin()][0])
            extRight = tuple(c[c[:, :, 0].argmax()][0])
          #  extTop = tuple(c[c[:, :, 1].argmin()][0])
          #  extBot = tuple(c[c[:, :, 1].argmax()][0])
            print(cv2.contourArea(c))
            if extRight[0] > maxx:
                maxx = extRight[0]
                self._hitcoords = extRight

        # Get the scores

        self._score = self._boardarray.getscore(self._hitcoords)

        return self._hitcoords, self._score  #Return tuple with coordinates and integer for score


    def draw(self, frame):
        #Mark the hit in the frame and write the score
        if not self._hitcoords == None:
            cv2.circle(frame, self._hitcoords, 5, (255, 0, 255), 4)
            cv2.putText(frame, str(self._score), self._hitcoords, cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 255), 10)
        return frame


    def __str__(self):
        return (str(self._score))



if __name__ == '__main__':
    print ("Testcode for DartHit")
    dh = DartHit()
    hitframe = cv2.imread(r"C:\Users\par\OneDrive\Documents\GitHub\DartScore\Testdata\ddframe2.jpg",cv2.IMREAD_UNCHANGED)
    conimg = hitframe.copy()

    hit, score = dh.update(hitframe)
    print (hit, score)
    print()

    conimg= dh.draw(conimg)

    cv2.imshow("Hitframe", hitframe)
    cv2.imshow("Contours", conimg)
   # cv2.imshow("Frame Delta", frameDelta)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        # cleanup the camera and close any open windows
        cv2.destroyAllWindows()
