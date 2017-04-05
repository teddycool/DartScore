__author__ = 'teddycool'
#Master class for the vision system, using other classes for each type of detection
#
#Webinfo used for this part of project:
# http://blog.miguelgrinberg.com/post/stream-video-from-the-raspberry-pi-camera-to-web-browsers-even-on-ios-and-android
import os
import sys
import time

import cv2

import Cam

try:
    from DartScoreEngineConfig import dartconfig
except: #Used when unittesting...
     dartconfig ={                   #Config for test-purpose
                "cam": {"res":(640, 480), "id":1, "framerate": 20},
                "Streamer": {"StreamerImage": "/tmp/stream/pic.jpg", "StreamerLib": "/tmp/stream", "VideoFile": "/home/pi/DartScore/video.mpg"},
         "Vision": {"WriteFramesToSeparateFiles": False, "PrintFrameRate": True, "RecordRaw": False, "RecordCv": False, "CamType": "PC"}}

class Vision(object):

    def __init__(self):
        print "Vision object started..."
        self._seqno = 0
        self._cam = Cam.createCam(dartconfig["Vision"]["CamType"])
        #TODO: check that streamer is running


    def initialize(self):
        print "Vision initialised"
        print "Starting streamer..."

        print os.system('sudo mkdir /tmp/stream')
        print os.system('sudo LD_LIBRARY_PATH=/home/pi/DartScore/mjpg-streamer/mjpg-streamer  /home/pi/DartScore/mjpg-streamer/mjpg-streamer/mjpg_streamer -i "input_file.so -f /tmp/stream -n pic.jpg" -o "output_http.so -w /home/pi/DartScore/mjpg-streamer/mjpg-streamer/www" &')

        self._cam.initialize()

        filenameraw = "dartscoreRaw_" + time.strftime("%Y%m%d_%H%M%S") + ".avi"
        filenamecv = "dartscoreCv_" + time.strftime("%Y%m%d_%H%M%S") + ".avi"
        #Two videowriters...
        if dartconfig["Vision"]["RecordRaw"]:
            self._videowraw = cv2.VideoWriter(dartconfig["Recorder"]["VideoFileDir"]+filenameraw, cv2.VideoWriter_fourcc(*'XVID'), 2, resolution )
        if dartconfig["Vision"]["RecordCv"]:
            self._videowcv = cv2.VideoWriter(dartconfig["Recorder"]["VideoFileDir"] + filenamecv,cv2.VideoWriter_fourcc(*'XVID'), 2, resolution)

    def update(self):
        frame = self._cam.update()
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

        #Write to actual frame for MJPG streamer
        #TODO: use a ram-disk for this file
        cv2.imwrite(dartconfig["Streamer"]["StreamerImage"],frame)

        if dartconfig["Vision"]["WriteFramesToSeparateFiles"]:
            #pickle.dump(self._contourFinder._cnts,open('cv2cnts' +str(self._seqno),'wb'))
            cv2.imwrite("cv2seq"+str(self._seqno)+".jpg",frame)
            self._seqno=self._seqno+1
        #Writing to opencv managed stream (same as to 'netcam')
            if dartconfig["Vision"]["RecordCv"]:
                self._videowcv.write(frame)

    def __del__(self):
        print "Vision object deleted..."
        if dartconfig["Vision"]["RecordRaw"]:
            self._videowraw = None
        if dartconfig["Vision"]["RecordCv"]:
            self._videowcv = None




if __name__ == '__main__':
    print "Testcode for Vision"

    vision= Vision()
    vision.initialize()
    if dartconfig["Vision"]["CamType"]== "PC":
        frame = vision.update()
        cv2.imshow('simple', frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    elif  dartconfig["Vision"]["CamType"]== "PI":

        try:
            while 1:
                print "Updating frame..."
                frame = vision.update()
                print "TypeOfFrame: " + str(type(frame))
                print "Drawing frame..."
                vision.draw(frame, 2)
                time.sleep(0.2)
        except:
            e = sys.exc_info()[0]
            print e
