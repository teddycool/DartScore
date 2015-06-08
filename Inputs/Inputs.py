__author__ = 'psk'
import Main
import pygame
import sys
from GuiComponents import Button
from pygame.locals import *
import Board

class Inputs(object):
    def __init__(self,mainloop):
        self.mainloop=mainloop
        self.forward = 0
        self.sideways = 0

    def initialize(self):
        #Array/collection of buttons
        self.Buttons={}

        self.Buttons["Exit"] = Button.Button((760,5,35, 35))
        self.Buttons["Exit"].color=(0,0,0,0)
        self.Buttons["Exit"].iconFg= pygame.image.load("icons/Frame_Exit.png")
        self.Buttons["Exit"].callback = sys.exit

        self.Buttons["Cal"] = Button.Button((605,545,150, 50))
        self.Buttons["Cal"].color=(0,0,0,0)
        self.Buttons["Cal"].iconFg= pygame.image.load("icons/Frame_Exit.png")
        self.Buttons["Cal"].text = "Setup Board"
        self.Buttons["Cal"].callback = sys.exit

    def update(self):
        self.forward = 0
        self.sideways = 0
        if pygame.key.get_pressed()[pygame.K_UP]!=0:
            self.forward = 1
        elif pygame.key.get_pressed()[pygame.K_DOWN]!=0:
            self.forward = -1

        if pygame.key.get_pressed()[pygame.K_LEFT] != 0:
            self.sideways = 1
        elif pygame.key.get_pressed()[pygame.K_RIGHT] != 0:
            self.sideways = -1
        else:
            self.sideways = 0

        pos=(0,0)
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit()


            if(event.type is MOUSEBUTTONDOWN):
                pos = pygame.mouse.get_pos()

                for button in self.Buttons:
                    if self.Buttons[button].selected(pos) == True:
                        self.Buttons[button].selectedImage = self.Buttons[button].iconFgPressed

                if(event.type is MOUSEBUTTONUP):
                    for button in self.Buttons:
                        self.Buttons[button].selectedImage = self.Buttons[button].iconFg
        return pos

    def draw(self, screen):
        for button in self.Buttons:
            self.Buttons[button].draw(screen)
        return screen


    def setMode(self, mode):
        self.mainloop.mode=mode;

    def calibrate(self):
        return

    def changePlayer(self, newPlayer):
        return

