__author__ = 'teddycool'
import cv2

try:
    from DartScoreEngineConfig import dartconfig
except:
     dartconfig ={                   #Config for test-purpose
                "cam": {"res":(640, 480), "id":1, "framerate": 20},
                "Streamer": {"StreamerImage": "/tmp/stream/pic.jpg", "StreamerLib": "/tmp/stream", "VideoFile": "/home/pi/DartScore/video.mpg"},
                 "Vision": {"WriteFramesToSeparateFiles": False, "PrintFrameRate": True, "RecordRaw": False, "RecordCv": False, "CamType": "PC"}}


def createCam(camtype):
    if camtype == "PC":
        import PcCam
        cam = PcCam.PcCam()
        return cam
    elif camtype == "PI":
        import PiCam
        cam = PiCam.PiCam()
        return cam





if __name__ == '__main__':
    print "Testcode for Cam"

    cam= createCam(dartconfig["Vision"]["CamType"])
    cam.initialize()
    frame = cam.update()

    cv2.imshow('simple',frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()