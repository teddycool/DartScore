__author__ = 'teddycool'
#Master class for the vision system, using other classes for each type of detection
#
#Webinfo used for this part of project:
# http://blog.miguelgrinberg.com/post/stream-video-from-the-raspberry-pi-camera-to-web-browsers-even-on-ios-and-android
import time
import picamera
#import picamera.array
from picamera.array import PiRGBArray
import cv2
import sys
import numpy as np
import os
import ContourFinder
import pickle
try:
    from DartScoreConfig import dartconfig
except:
     dartconfig ={                   #Config for test-purpose
                "cam": {"res":(640, 480), "id":1, "framerate": 20},
                "Streamer": {"StreamerImage": "/tmp/stream/pic.jpg", "StreamerLib": "/tmp/stream", "VideoFile": "/home/pi/DartScore/video.mpg"},
                "Vision": {"WriteFramesToSeparateFiles": False, "PrintFrameRate": True}
     }

class Vision(object):

    def __init__(self):
        print "Vision object started..."
        self._seqno = 0
        #self._contourFinder = ContourFinder.ContourFinder()

        #TODO: check that streamer is running


    def initialize(self):
        print "Vision initialised"
        print "Starting streamer..."

        print os.system('sudo mkdir /tmp/stream')
        print os.system('sudo LD_LIBRARY_PATH=/home/pi/mjpg-streamer/mjpg-streamer /home/pi/mjpg-streamer/mjpg-streamer/mjpg_streamer -i "input_file.so -f /tmp/stream -n pic.jpg" -o "output_http.so -w /home/pi/mjpg-streamer/mjpg-streamer/www" &')

        #CAM stettings! exposure, wb etc or try using pygame.cam?
        #https://picamera.readthedocs.org/en/release-1.10/recipes1.html#capturing-consistent-images
        print "CAM init..."
        resolution = dartconfig["cam"]["res"]
        self._cam = picamera.PiCamera()
        self._cam.resolution = resolution
        self._center = (resolution[0]/2, resolution[1]/2)
        self._cam.framerate = dartconfig["cam"]["framerate"]
        print "Wait for the automatic gain control to settle"
        time.sleep(2)
        print "Setting cam fix values"
        # Now fix the values
        self._cam.shutter_speed = self._cam.exposure_speed
        self._cam.exposure_mode = 'off'
        g = self._cam.awb_gains
        self._cam.awb_mode = 'off'
        self._cam.awb_gains = g
        self._lastframetime = time.time()
        self._rawCapture = PiRGBArray(self._cam, size=resolution)
        self._imagegenerator = self._cam.capture_continuous(self._rawCapture, format="bgr", use_video_port=True)
        #self._contourFinder.initialize()
        #frame =  self.update()
       # self._videow = cv2.VideoWriter(dartconfig["Streamer"]["VideoFile"], cv2.cv.CV_FOURCC('P','I','M','1'), 20, resolution )

    def update(self):
        #TODO: make threaded in exception catcher
        rawframe = self._imagegenerator.next()
        self._rawCapture.truncate()
        self._rawCapture.seek(0)
        frame = rawframe.array
        #self._contourFinder.update(frame)
        if dartconfig["Vision"]["WriteFramesToSeparateFiles"]:
            cv2.imwrite("camseq"+str(self._seqno)+".jpg",frame)
        return frame

    def draw(self, frame, framerate):
        #self._contourFinder.draw(frame)
        if dartconfig["Vision"]["PrintFrameRate"]:
            cv2.putText(frame, "Framerate: " + str(framerate), (5,150),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

        #Write to actual frame for MJPG streamer
        cv2.imwrite(dartconfig["Streamer"]["StreamerImage"],frame)

        if dartconfig["Vision"]["WriteFramesToSeparateFiles"]:
            #pickle.dump(self._contourFinder._cnts,open('cv2cnts' +str(self._seqno),'wb'))
            cv2.imwrite("cv2seq"+str(self._seqno)+".jpg",frame)
            self._seqno=self._seqno+1


    def __del__(self):
        print "Vision object deleted..."
        self._cam.close()




if __name__ == '__main__':
    print "Testcode for Vision"

    vision= Vision()
    vision.initialize()
    try:
        while 1:
            print "Updating frame..."
            frame = vision.update()
            print "Drawing frame..."
            vision.draw(frame)
            time.sleep(0.2)
    except:
        e = sys.exc_info()[0]
        print e
