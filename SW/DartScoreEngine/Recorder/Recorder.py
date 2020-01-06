__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore

# Purpose of this file:
# Record anything from a img stream to a videofile

import time

from cv2 import cv2

#from DartScoreEngineConfig import dartconfig


class Recorder(object):

    def __init__(self, videodir, res):
        print ("Recorder object started...")
        self._seqno = 0
        self._recording= False
        #self._states["IDLE","START", "REC", "STOP"]
        self._state = "IDLE"
        self._videow = None
        self._framecount = 0
        self._videodir = videodir
        self._res = res


    def initialize(self):
        print ("Recorder initialised with state " )+ self._state


    def update(self, rec):
        #The statemachine for recording...
        if rec:
            if self._state == "IDLE":
                self._state = "START"
            elif self._state == "START":
                self._state = "REC"
            # -> Keep REC if still motion detected but abort if maxframes is reached
            elif self._state == "STOP":
                self._state = "IDLE"

        if not rec:
            if self._videow is not None:
                print ("Stopping recording from " + self._state + " state and closing file")
                self._framecount = 0
                self._videow = None
            if self._state == "REC":
                self._state = "STOP"
            elif self._state == "START":
                self._state = "STOP"
            else:
                self._state = "IDLE"

        return self._state

    def draw(self, frame, fr):
        #Write recorder string to frame
        #cv2.putText(frame, time.strftime("%Y-%m-%d %H:%M:%S"), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255, 255, 255), 2)

        if self._state == "START":
            print ("Start recording")
            filename = r"/dartscore_" + time.strftime("%Y%m%d_%H%M%S") + ".avi"
            self._videow = cv2.VideoWriter(self._videodir + filename,
                                           cv2.VideoWriter_fourcc(*'XVID'), int(fr),
                                           self._res, True)
            self._videow.write(frame)
            print ("Starting videofile: " + filename)
            cv2.putText(frame, "rec", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        elif self._state == "REC":
            self._videow.write(frame)
            self._framecount = self._framecount+1
            cv2.putText(frame, "rec " + str(self._framecount) , (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1 , (0, 0, 255), 2)

        elif self._state == "STOP":
            self._framecount = 0

        return frame


if __name__ == "__main__":
    import numpy as np
    import Cam
    #recorder = Recorder(r'C:\Users\par\OneDrive\Documents\GitHub\DartScore\Testdata\Videos', (500,500))
    recorder = Recorder(r'C:\Users\par\OneDrive\Documents\GitHub\DartScore\Testdata\Videos', (1024, 768))

    cam = Cam.createCam("STREAM")
    cam.initialize('http://192.168.1.131:8081')
    # transform = np.float32(
    #     [[1.78852294e+00, -1.10143263e-01, -4.85063747e+02], [2.17855239e-01, 1.03682933e+00, -3.82665632e+01],
    #      [1.28478485e-03, -1.58506840e-04, 1.00000000e+00]])
    # cam.settransformmatrix(transform)
    
    while True:
        img = cam.update()
        recorder.update(True)
        img = recorder.draw(img, 5)
        cv2.imshow('Recording this...', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    recorder.update(False)
    cv2.destroyAllWindows()



