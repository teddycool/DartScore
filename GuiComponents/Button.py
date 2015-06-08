__author__ = 'psk'
# Button is a simple tappable screen region.  Each has:
#  - bounding rect ((X,Y,W,H) in pixels)
#  - optional background color and/or Icon (or None), always centered
#  - optional foreground Icon, always centered
#  - optional single callback function
#  - optional single value passed to callback
# Occasionally Buttons are used as a convenience for positioning Icons
# but the taps are ignored.  Stacking order is important; when Buttons
# overlap, lowest/first Button in list takes precedence when processing
# input, and highest/last Button is drawn atop prior Button(s).  This is
# used, for example, to center an Icon by creating a passive Button the
# width of the full screen, but with other buttons left or right that
# may take input precedence (e.g. the Effect labels & buttons).
# After Icons are loaded at runtime, a pass is made through the global
# buttons[] list to assign the Icon objects (from names) to each Button.
import pygame
class Button:
    def __init__(self, rect, **kwargs):
      self.rect     = rect # Bounds
      self.color    = None # Background fill color, if any
      self.iconBg   = None # Background Icon (atop color fill)
      self.iconFg   = None # Foreground Icon (atop background)
      self.iconFgPressed = None
      self.selectedImage = None
      self.bg       = None # Background Icon name
      self.fg       = None # Foreground Icon name
      self.fgPressed = None
      self.callback = None # Callback function
      self.value    = None # Value passed to callback
      self.text = ""
      for key, value in kwargs.iteritems():
        if   key == 'color': self.color    = value
        elif key == 'bg'   : self.bg       = value
        elif key == 'fg'   : self.fg       = value
        elif key == 'cb'   : self.callback = value
        elif key == 'value': self.value    = value

    def selected(self, pos):
      x1 = self.rect[0]
      y1 = self.rect[1]
      x2 = x1 + self.rect[2] - 1
      y2 = y1 + self.rect[3] - 1
      if ((pos[0] >= x1) and (pos[0] <= x2) and
          (pos[1] >= y1) and (pos[1] <= y2)):
        if self.callback:
            if self.value is None:
                self.callback()
            else:
              self.callback(self.value)
        self.selectedImage = self.iconFgPressed
        return True
      self.selectedImage = self.iconFg
      return False

    def draw(self, screen):
      if self.color:
        screen.fill(self.color, self.rect)
      if self.iconBg:
        screen.blit(self.iconBg.bitmap,
          (self.rect[0]+(self.rect[2]-self.iconBg.bitmap.get_width())/2,
           self.rect[1]+(self.rect[3]-self.iconBg.bitmap.get_height())/2))
      if self.iconFg:
        if self.selectedImage == None:
            self.selectedImage = self.iconFg
        screen.blit(self.selectedImage,
          (self.rect[0]+(self.rect[2]-self.iconFg.get_width())/2,
           self.rect[1]+(self.rect[3]-self.iconFg.get_height())/2))

      myFontSize = 30
      myfont = pygame.font.SysFont("Arial", myFontSize)
      label = myfont.render(self.text, 1, (255,255,255))
      posX = self.rect[0]+(self.rect[2]-self.iconFg.get_width())/2 + 10
      posY = self.rect[1]+(self.rect[3] / 2) - (myFontSize / 2)
      screen.blit(label, (posX,posY))

    def setBg(self, name):
      if name is None:
        self.iconBg = None
      else:
        for i in icons:
          if name == i.name:
            self.iconBg = i
            break
