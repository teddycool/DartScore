__author__ = 'teddycool'
# Propose of this module is to create and return a 'cam'-device for the selected environment
# Cam is used for delivering a videostream of the dartboard


def createCam(camtype):
    if camtype == "PC":
        from WinSetup.PcCam import PcCam
        cam = PcCam()
        return cam
    elif camtype == "PI":
        from PiSetup.PiCam import PiCam
        cam = PiCam()
        return cam
    elif camtype == "VIDEO":
        from WinSetup.VideoCam import  VideoCam
        cam = VideoCam()
        return cam

