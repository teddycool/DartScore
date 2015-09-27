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
import LaserFinder
import ContourFinder
import FaceDetector
import os
from config import roverconfig


class Vision(object):

    def __init__(self, resolution):
        print "Vision object started..."
        self._contourFinder = ContourFinder.ContourFinder()
        self._faceDetector = FaceDetector.FaceDetector()
        self._cam = picamera.PiCamera()
        self._cam.resolution = resolution
        self._center = (resolution[0]/2, resolution[1]/2)
        self._laserfinder = LaserFinder.LaserFinder()
        #TODO: check that streamer is running


    def initialize(self):
        self._cam.start_preview()
        self._faceDetector.initialize(scaleFactor= 1.1 , minNeighbors= 5, minSize=(60, 60) ,flags=cv2.CASCADE_SCALE_IMAGE )
        self._laserfinder.initialize()


    def update(self):
         #TODO: make threaded in exception catcher
        stream = picamera.array.PiRGBArray(self._cam)
        self._cam.capture(stream, format='bgr')
        # At this point the image is available as stream.array
        frame = stream.array
        self._contourFinder.update(frame)
        self._faceDetector.update(frame)
        self._laserfinder.update(frame)
        return frame

    def draw(self, frame):
        frame = self._contourFinder.draw(frame)
        frame = self._faceDetector.draw(frame)
        frame = self._laserfinder.draw(frame)

        #draw cross for center of image
        cv2.line(frame,(self._center[0]-20,self._center[1]),(self._center[0]+20, self._center[1]),(255,255,255),2)
        cv2.line(frame,(self._center[0],self._center[1]-20),(self._center[0],self._center[1]+20),(255,255,255),2)
        cv2.line(frame, self._laserfinder._point, self._center,(0,255,0),2)
        cv2.putText(frame,"Streamer: " + roverconfig["Streamer"]["StreamerImage"], (5,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

        #Draw to streamer lib to 'publish'
        #TODO: move to mainloop and make threaded
        cv2.imwrite(roverconfig["Streamer"]["StreamerImage"],frame)

        #TODO: set up a defined framerate
        time.sleep(0.1)

    def __del__(self):
        print "Vision object deleted..."
        self._cam.close()




if __name__ == '__main__':
    print "Testcode for Vision"
    import RPi.GPIO as GPIO
    import Laser
    GPIO.setmode(GPIO.BCM)
    laser = Laser.Laser(GPIO, 21)
    laser.activate(True)

    vision= Vision( (640,480))
    vision.initialize()
    try:
        while 1:
            #print "Updating frame..."
            frame = vision.update()
            #print "Drawing frame..."
            vision.draw(frame)
            time.sleep(0.2)
    except:
        laser.activate(False)
        GPIO.cleanup()
        e = sys.exc_info()[0]
        print e
