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
        resolution = dartconfig["cam"]["res"]
        self._cam = picamera.PiCamera()
        self._cam.resolution = resolution
        self._center = (resolution[0]/2, resolution[1]/2)
        #TODO: check that streamer is running


    def initialize(self):
        print "CAM init..."


    def update(self):
         #TODO: make threaded in exception catcher
        stream = picamera.array.PiRGBArray(self._cam)
        self._cam.capture(stream, format='bgr')
        # At this point the image is available as stream.array
        frame = stream.array
        return frame

    def draw(self, frame):
        cv2.imwrite(dartconfig["Streamer"]["StreamerImage"],frame)
        #time.sleep(1/dartconfig['framerate'])


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
