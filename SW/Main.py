__author__ = 'teddycool'
# Main for the DartScore project

import sys
import pygame

sys.path.append("/home/pi/DartScore/SW")

import time

import MainLoop


class Main(object):

    def __init__(self):
        print ("Init Main object...")
        self._mainLoop= MainLoop.MainLoop()


    def run(self):
        self._mainLoop.initialize()
        stopped = False
        while not stopped:
            framestarttime = time.time()
            frame = self._mainLoop.update()
            self._mainLoop.draw(frame)
            #time.sleep(0.01)
            #TODO: handle keyboard interupt exception
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    stopped = True

        pygame.quit()


if __name__ == "__main__":
    gl=Main()
    gl.run()
