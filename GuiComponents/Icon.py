__author__ = 'teddycool'
# Icon is a very simple bitmap class, just associates a name and a pygame
# image (PNG loaded from icons directory) for each.
# There isn't a globally-declared fixed list of Icons.  Instead, the list
# is populated at runtime from the contents of the 'icons' directory.
import pygame
class Icon:
	def __init__(self, name):
	  self.name = name
	  try:
	    self.bitmap = pygame.image.load(name + '.png')
	  except:
	    pass