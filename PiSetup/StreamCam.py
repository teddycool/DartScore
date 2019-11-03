__author__ = 'teddycool'
import time

import cv2
from urllib.request import urlopen
import numpy as np

try:
    from DartScoreEngine.DartScoreEngineConfig import dartconfig
except:
     dartconfig ={                   #Config for test-purpose
                "cam": {"res":(640, 480), "id":1, "framerate": 20},
                "Streamer": {"StreamerImage": "/tmp/stream/pic.jpg", "StreamerLib": "/tmp/stream", "VideoFile": "/home/pi/DartScore/video.mpg"},
                "Vision": {"WriteFramesToSeparateFiles": False, "PrintFrameRate": True, "RecordRaw": False, "RecordCv": False}}

class StreamCam(object):

    def __int__(self):
        self._camId = 0

    def initialize(self):
        print ("Stream CAM init...")
        resolution = dartconfig["cam"]["res"]
        #self._cam.framerate = dartconfig["cam"]["framerate"]
        self._actualFrameRate = 0
        self._lastFrameTime = time.time()
        self._stream = urlopen('http://192.168.1.18:8081')
        self._bytes = bytearray()
        
        #self._imagegenerator = self._cam.capture_continuous(self._rawCapture, format="bgr", use_video_port=True)

    def update(self):
        while True:
            self._bytes += self._stream.read(1024)
            a = self._bytes.find(b'\xff\xd8')
            b = self._bytes.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = self._bytes[a:b+2]
                self._bytes = self._bytes[b+2:]
                frame = cv2.cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.cv2.IMREAD_COLOR)
                self._actualFrameRate = 1/(time.time()- self._lastFrameTime)
                self._lastFrameTime = time.time()
                return frame
        # Write to 'raw-video* coming directly from cam
        

    

if __name__ == '__main__':
    print ("Testcode for StreamCam")
    cam = StreamCam()
    cam.initialize()

    while True:
        img = cam.update()
        cv2.cv2.imshow('Video', img)
        if cv2.cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.cv2.destroyAllWindows()






