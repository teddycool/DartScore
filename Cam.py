__author__ = 'teddycool'
import cv2
import time


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




if __name__ == '__main__':
    print "Testcode for Cam"
    cam = createCam("VIDEO")
    cam.initialize()

    while True:
        frame = cam.update()
        if frame == None:
            break
        cv2.imshow("Tracking", frame)
        time.sleep(0.1)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()