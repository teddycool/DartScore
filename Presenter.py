__author__ = 'teddycool'
import cv2
import time


def createPresenter(type):
    if type == "PC":
        from WinSetup.VideoPresenter import VideoPresenter
        presenter = VideoPresenter()
        return presenter
    elif type == "PI":
        from PiSetup.VideoPresenter import  VideoPresenter
        presenter = VideoPresenter()
        return presenter
    elif type == "VIDEO":
        from WinSetup.VideoPresenter  import VideoPresenter
        presenter = VideoPresenter()
        return presenter



if __name__ == '__main__':
    print "Testcode for Cam"
    pres = createPresenter("VIDEO")
    pres.initialize()

    while True:
        frame = cam.update()
        if frame == None:
            break
        cv2.imshow("Tracking", frame)
        time.sleep(0.1)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()