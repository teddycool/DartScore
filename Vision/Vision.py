__author__ = 'teddycool'
#Master class for the vision system, using other classes for each type of detection
#
#Webinfo used for this part of project:
# http://blog.miguelgrinberg.com/post/stream-video-from-the-raspberry-pi-camera-to-web-browsers-even-on-ios-and-android
import time
import picamera
import picamera.array
import cv2
import sys
import numpy as np
from DartScoreConfig import dartconfig

class Vision(object):

    def __init__(self):
        print "Vision object started..."
        self._seqno = 0

        #TODO: check that streamer is running


    def initialize(self):
        #CAM stettings! exposure, wb etc or try using pygame.cam?
        #https://picamera.readthedocs.org/en/release-1.10/recipes1.html#capturing-consistent-images
        print "CAM init..."
        resolution = dartconfig["cam"]["res"]
        self._cam = picamera.PiCamera()
        self._cam.resolution = resolution
        self._center = (resolution[0]/2, resolution[1]/2)
        self._cam.framerate = dartconfig["cam"]["framerate"]
        # Wait for the automatic gain control to settle
        time.sleep(2)
        # Now fix the values
        self._cam.shutter_speed = self._cam.exposure_speed
        self._cam.exposure_mode = 'off'
        g = self._cam.awb_gains
        self._cam.awb_mode = 'off'
        self._cam.awb_gains = g
        frame =  self.update()
       # self._videow = cv2.VideoWriter(dartconfig["Streamer"]["VideoFile"], cv2.cv.CV_FOURCC('P','I','M','1'), 20, resolution )

    def update(self):
        #TODO: make threaded in exception catcher
        stream = picamera.array.PiRGBArray(self._cam)
        self._cam.capture(stream, format='bgr')
        # At this point the image is available as stream.array
        frame = stream.array
        if dartconfig["Vision"]["WriteFramesToSeparateFiles"]:
            cv2.imwrite("camseq"+str(self._seqno)+".jpg",frame)
        return frame

    def draw(self, frame, framerate):
        if dartconfig["Vision"]["PrintFrameRate"]:
            cv2.putText(frame, "Framerate: " + str(framerate), (5,150),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

        #Write to actual frame for MJPG streamer
        cv2.imwrite(dartconfig["Streamer"]["StreamerImage"],frame)

        if dartconfig["Vision"]["WriteFramesToSeparateFiles"]:
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
