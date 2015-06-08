__author__ = 'psk'
import pygame

class CamCalibrateLoop(object):
    def __init__(self):
        return

    def initialize(self):
        self._centerRect = pygame.Rect(200, 280, 80, 80)
        return

    def update(self, screen):
        return screen

    def draw(self, snapshot):
        #draw rect for center of snapshot
        snapshot= pygame.draw.rect(snapshot, (255,0,0), self._centerRect, width=3)
        return snapshot