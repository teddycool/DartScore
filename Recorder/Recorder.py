__author__ = 'teddycool'

import time
import cv2
import os
from DartScoreConfig import dartconfig

class Recorder(object):

    def __init__(self):
        print "Recorder object started..."
        self._seqno = 0
        self._recording= False
        #self._states["IDLE","START", "REC", "STOP"]
        self._state = "IDLE"
        self._videow = None
        self._framecount = 0


    def initialize(self):
        print "Recorder initialised with state " + self._state


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
                print "Stopping recording from " + self._state + " state and closing file"
                self._framecount = 0
                self._videow = None
            if self._state == "REC":
                self._state = "STOP"
            elif self._state == "START":
                self._state = "STOP"
            else:
                self._state = "IDLE"

        return self._state

    def draw(self, frame,fr):
        #Write recorder string to frame
        #cv2.putText(frame, time.strftime("%Y-%m-%d %H:%M:%S"), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
         #           (255, 255, 255), 2)

        if self._state == "START":
            print "Start recording"
            filename = "dartscore_" + time.strftime("%Y%m%d_%H%M%S") + ".avi"
            self._videow = cv2.VideoWriter(dartconfig["Recorder"]["VideoFileDir"] + filename,
                                           cv2.VideoWriter_fourcc(*'XVID'), int(fr),
                                           dartconfig["cam"]["res"], True)
            self._videow.write(frame)
            print "Starting videofile: " + filename
            cv2.putText(frame, "rec", (900, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        elif self._state == "REC":
            self._videow.write(frame)
            self._framecount = self._framecount+1
            cv2.putText(frame, "rec " + str(self._framecount) , (900, 30), cv2.FONT_HERSHEY_SIMPLEX, 1 , (0, 0, 255), 2)

        elif self._state == "STOP":
            self._framecount = 0

        return frame

