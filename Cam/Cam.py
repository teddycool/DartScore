__author__ = 'psk'
import pygame

class Cam(object):
    def __init__(self):
        print "Cam __init__"
        self.camid=1
        self.width= 640
        self.height=480


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
    #Set to webcam ID, std is 0. Networkedcam is probably 1
    camid=1
    #Set to resolution of your webcam 1280x 720
    width= 1280
    height=720
    gl=MainLoop(width,height, camid)
    gl.run()