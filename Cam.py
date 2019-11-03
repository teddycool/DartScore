__author__ = 'teddycool'
# Propose of this module is to create and return a 'cam'-device for the selected environment
# Cam is used for delivering a videostream of the dartboard


def createCam(camtype):
    if camtype == "STREAM":
        from PiSetup.StreamCam import  StreamCam
        cam = StreamCam()
        return cam

