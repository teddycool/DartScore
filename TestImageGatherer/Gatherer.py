__author__ = 'psk'

import pygame.camera
import time
import pygame
import sys
from GuiComponents import Button
from pygame.locals import *

class Gatherer(object):

    def __init__(self, camid, cwidth, cheigth):
        print "Main __init__"
        self.camid = camid
        self.dwidth = cwidth
        self.dheight = cheigth

    def run(self):

        #Init and set up variables...
        pygame.init()
        pygame.camera.init()
        cam = pygame.camera.Camera(self.camid,(self.dwidth,self.dheight),"RGB")
        Buttons = {}
        self.display = pygame.display.set_mode((self.dwidth,self.dheight))
        print pygame.display.Info()

        Buttons["Exit"] = Button.Button((270,380,100, 100))
        Buttons["Exit"].color=(0,0,0,0)
        Buttons["Exit"].iconFg= pygame.image.load("stop.png")
        Buttons["Exit"].callback = sys.exit

        snapshot = pygame.surface.Surface((self.dwidth,self.dheight),0)

        print "Starting program evaluation loop"
        seq = 0
        running = True
        pause = False
        while  running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if(event.type is MOUSEBUTTONDOWN):
                    pos = pygame.mouse.get_pos()
                    if Buttons['Exit'].selected(pos) == True:
                        running = False
                    else:
                        if not pause:
                            pause = True
                        else:
                            pause = False


            black=0,0,0
            self.display.fill(black)
            snapshot.fill(black)

            if not pause:
                snapshot = cam.get_image(snapshot)
                seq = seq+1
                pygame.image.save(snapshot, "collected//seq" + str(seq) + ".jpg")

            Buttons['Exit'].draw(snapshot)
            self.display.blit(snapshot,(0,0))
            pygame.display.flip()
            t=0
            time.sleep(0.01)
        sys.exit()

if __name__ == "__main__":
    #Set to webcam ID, std is 0. Networked cam is probably 1
    camid=1
    #Set to resolution of your webcam
    width= 640
    height=480
    gl=Gatherer(camid,width,height)
    gl.run()