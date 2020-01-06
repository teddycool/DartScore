__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore

# Purpose of this file is to create and return a 'cam'-device
# The cam-device is then used for delivering a videostream of the dartboard that can be intepreted by opencv
# At present there is only one type of cam (the rest are removed) but I leave this as it is for now


def createCam(camtype):
    if camtype == "STREAM":
        from PiSetup.StreamCam import StreamCam
        cam = StreamCam()
        return cam
    if camtype == "VIDEO":
        from DartScoreEngine.Utils.VideoCam import VideoCam
        cam = VideoCam()
        return cam
    raise ("CamSelectionError")


