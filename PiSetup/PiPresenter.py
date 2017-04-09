__author__ = 'teddycool'

import cv2
import time
import os

class VideoPresenter(object):

    def __init__(self):
        self._windowname = "VideoPresenter"

        print os.system('sudo mkdir /tmp/stream')
        print os.system('sudo LD_LIBRARY_PATH=/home/pi/DartScore/mjpg-streamer/mjpg-streamer  /home/pi/DartScore/mjpg-streamer/mjpg-streamer/mjpg_streamer -i "input_file.so -f /tmp/stream -n pic.jpg" -o "output_http.so -w /home/pi/DartScore/mjpg-streamer/mjpg-streamer/www" &')



    def draw(self, frame):
        cv2.imwrite(dartconfig["Streamer"]["StreamerImage"], frame)


    def __del__(self):
        cv2.destroyAllWindows()


if __name__ == '__main__':
    print "Testcode for videpresenter"
    print cv2.__version__
    cam = cv2.VideoCapture("C:/Users/psk/Documents/GitHub/DartScore/Testdata/Videos/dartscoreRaw_20170327_193108.avi")
    pres = VideoPresenter()

    while True:
        ret, frame = cam.read()
        pres.draw(frame)
        time.sleep(0.5)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()
