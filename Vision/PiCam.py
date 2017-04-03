__author__ = 'teddycool'
import time

import picamera
from picamera.array import PiRGBArray

try:
    from DartScoreConfig import dartconfig
except:
     dartconfig ={                   #Config for test-purpose
                "cam": {"res":(640, 480), "id":1, "framerate": 20},
                "Streamer": {"StreamerImage": "/tmp/stream/pic.jpg", "StreamerLib": "/tmp/stream", "VideoFile": "/home/pi/DartScore/video.mpg"},
                "Vision": {"WriteFramesToSeparateFiles": False, "PrintFrameRate": True, "RecordRaw": False, "RecordCv": False}}

class PiCam(object):

    def __int__(self):
        self._camId = 0

    def initialize(self):
        print "PI CAM init..."
        resolution = dartconfig["cam"]["res"]
        self._cam = picamera.PiCamera()
        self._cam.resolution = resolution
        self._center = (resolution[0] / 2, resolution[1] / 2)
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

    def update(self):
        # TODO: make threaded in exception catcher
        rawframe = self._imagegenerator.next()
        self._rawCapture.truncate()
        self._rawCapture.seek(0)
        frame = rawframe.array
        # Write to 'raw-video* coming directly from cam
        return frame

    def __del__(self):
        self._cam.close()




