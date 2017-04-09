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
    from DartScoreEngine.DartScoreEngineConfig import dartconfig
except: #Used when unittesting...
     dartconfig ={                   #Config for test-purpose
                "cam": {"res":(640, 480), "id":1, "framerate": 20},
                "Streamer": {"StreamerImage": "/tmp/stream/pic.jpg", "StreamerLib": "/tmp/stream", "VideoFile": "/home/pi/DartScore/video.mpg"},
         "Vision": {"WriteFramesToSeparateFiles": False, "PrintFrameRate": True, "RecordRaw": False, "RecordCv": False, "CamType": "PC"}}

class Vision(object):

    def __init__(self, cam ):
        print "Vision object started..."
        self._seqno = 0
        self._cam = cam
        #TODO: check that streamer is running


    def initialize(self):
        print "Vision initialised"

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

    def __del__(self):
        print "Vision object deleted..."
        if dartconfig["Vision"]["RecordRaw"]:
            self._videowraw = None
        if dartconfig["Vision"]["RecordCv"]:
            self._videowcv = None




if __name__ == '__main__':
    print "Testcode for Vision"

    vision = Vision()
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
