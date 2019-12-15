__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore

# Purpose of this file:
# Master class for the vision system, using other classes for each type of detection#
# Webinfo used for this part of project:
# http://blog.miguelgrinberg.com/post/stream-video-from-the-raspberry-pi-camera-to-web-browsers-even-on-ios-and-android


import os
import sys
import time
from cv2 import cv2

from DartScoreEngine.DartScoreEngineConfig import dartconfig

class Vision(object):
    def __init__(self ):
        print ("Vision object started...")
        self._seqno = 0
        #TODO: check that streamer is running


    def initialize(self):
        print ("Vision initialised")

    def update(self, frame):
        if dartconfig["Vision"]["RecordRaw"]:
            self._videowraw.write(frame)
        #self._contourFinder.update(frame)
        if dartconfig["Vision"]["WriteFramesToSeparateFiles"]:
            cv2.imwrite("camseq"+str(self._seqno)+".jpg",frame)
        return frame

    def draw(self, frame, framerate):
        #self._contourFinder.draw(frame)
        if dartconfig["Vision"]["PrintFrameRate"]:
            cv2.putText(frame, "Framerate: " + str(framerate), (5,150),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

        if dartconfig["Vision"]["WriteFramesToSeparateFiles"]:
            #pickle.dump(self._contourFinder._cnts,open('cv2cnts' +str(self._seqno),'wb'))
            cv2.imwrite("cv2seq"+str(self._seqno)+".jpg",frame)
            self._seqno=self._seqno+1
        #Writing to opencv managed stream (same as to 'netcam')
            if dartconfig["Vision"]["RecordCv"]:
                self._videowcv.write(frame)
        return frame


    def __del__(self):
        print ("Vision object deleted...")
        if dartconfig["Vision"]["RecordRaw"]:
            self._videowraw = None
        if dartconfig["Vision"]["RecordCv"]:
            self._videowcv = None



if __name__ == '__main__':
    print ("Testcode for Vision")
    import os
    import sys
    #ap = cv2.VideoCapture(r'C:\Users\par\OneDrive\Documents\GitHub\DartScore\Testdata\Videos\dartscore_20191107_152701.avi')
    cap = cv2.VideoCapture(r'/home/pi/DartScore/Testdata/Videos/dartscore_20191107_152701.avi')
    vision = Vision()
    vision.initialize()
    
    if (cap.isOpened()== False): 
        print("Error opening video stream or file")
    
    cv2.namedWindow('Video', cv2.WINDOW_AUTOSIZE)
    # Read until video is completed
    while(cap.isOpened()):    # Capture frame-by-frame
                    
        ret, frame = cap.read()
        print(ret)
        print ("Updating frame...")
        frame = vision.update(frame)
        print ("TypeOfFrame: " + str(type(frame)))
        print ("Drawing frame...")
        frame = vision.draw(frame, 5)
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(0.2)

    cap.release()
    cv2.destroyAllWindows()
