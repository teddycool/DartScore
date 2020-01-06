__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore

# Purpose of this file:
# Create a stream of frames from a video file that can be used by opencv

import time

from cv2 import cv2
from urllib.request import urlopen
import numpy as np

from DartScoreEngine.DartScoreEngineConfig import dartconfig


class VideoCam(object):

    def __int__(self):
        self._camId = 0

    def initialize(self, fileurl, framerate=10):
        print("Video CAM init...")
        self._actualFrameRate = 0
        self._lastFrameTime = time.time()
        self._stream = cv2.VideoCapture(fileurl)
        self._transform = []
        self._fr = framerate

    def update(self):
        while True:
            # TODO: fix configurable cam res
            ret, frame = self._stream.read()
            time.sleep(1 / self._fr)
            if len(self._transform) == 0:
                return frame
            else:
                return cv2.warpPerspective(frame, self._transform, (500, 500))


    def settransformmatrix(self, matrix):
        self._transform = matrix


if __name__ == '__main__':
    print("Testcode for StreamCam")
    cam = VideoCam()
    cam.initialize(r'C:\Users\par\OneDrive\Documents\GitHub\DartScore\Testdata\Videos\dartscore_20191222_130118.avi')

    while True:
        img = cam.update()
        cv2.imshow('Video', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()






