__author__ = 'psk'

import pygame
import time

class Dart(object):

    def __init__(self, board):
        self._board = board
        #self._lasthit = pygame.rect



    def initialize(self):
        self._timeout = 5
        self._timelasthit = time.time()

    def update(self, hit):
        #check if hit and in which sector
        pass

    def draw(self, screen):
        #Draw mark for hit on the board if time since hit is less then timeout
        return screen


