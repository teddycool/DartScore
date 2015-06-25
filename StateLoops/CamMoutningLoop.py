_author__ = 'teddycool'
import pygame
from  StateLoop import StateLoop

class CamMountingLoop(StateLoop):
    def __init__(self):
        super(CamMountingLoop, self).__init__()
        return

    def initialize(self):
        self._centerRect = pygame.Rect(245, 215, 150, 50)
        return

    def update(self, screen):
        return screen

    def draw(self, snapshot):
        #draw rect for center of snapshot
        pygame.draw.rect(snapshot, (0,255,0), self._centerRect, 5)
        pygame.draw.circle(snapshot, (255,0,0), (320,240), 3, 0)
        return snapshot