__author__ = 'teddycool'
import pygame
import pygame.camera
import DartScoreConfig

class Cam(object):
    def __init__(self):
        print "Cam __init__"
        self.camid= DartScoreConfig.config['cam']['id']
        self.width, self.height= DartScoreConfig.config['cam']['res']


    def initialize(self):
        print "Cam initialize: " + str(self.camid)
        #Init and set up variables...
        pygame.camera.init()
        self.csnapshot = pygame.surface.Surface((self.width,self.height),0) #current frame
        self.psnapshot = pygame.surface.Surface((self.width,self.height),0) #previous frame
        self.cam = pygame.camera.Camera(self.camid,(self.width,self.height),"RGB")

    def update(self):
        #update each loop
        self.psnapshot = self.csnapshot
        self.csnapshot = self.cam.get_image(self.csnapshot)
        return self.csnapshot


    def draw(self, screen):
        #draw each loop
        return

if __name__ == "__main__":

    print pygame.surfarray.get_arraytype()
    import cv2
    import time
    cam=Cam()
    cam.initialize()
    snapshot = cam.update()
    #time.sleep(5)
    img=pygame.surface.Surface((cam.width,cam.height),0)
    t=0
    while t < 100:
        snapshot = cam.update()
        t= t+1
    snapshot = pygame.transform.rotate(snapshot,90)
    snapshot = pygame.transform.flip(snapshot, 0, 1)
    cv2.imshow('img',pygame.surfarray.pixels3d(snapshot))
    cv2.waitKey(0)
    cv2.destroyAllWindows()