try:
    import sys
    import random
    import math
    import os
    import getopt
    import pygame
    from socket import *
    from pygame.locals import *
except ImportError as err:
    print("Couldn't load module: {}.".format(err))
    sys.exit(2)




pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1, 1), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption('Burglar')

screen = pygame.display.set_mode((1350, 1000), pygame.HWSURFACE | pygame.DOUBLEBUF)
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 0))

from enum import Enum
from utils import write
from utils import colorScheme


class ListMenu:

    def __init__(self):
        self.options = ('easy', 'normal', 'hard', 'options', 'help')
        self.selected = 0
        self.align = 'right'
        self.font = 'Multicolore.otf'
        self.fontDefault = {'size': 53, 'color': colorScheme.MENUINACTIVE}
        self.fontSelected = {'size': 68, 'color': colorScheme.MENUACTIVE}
        self.prepare()
        self.menuFrame = pygame.Surface((self.menuWidth, self.menuHeight)).convert()

    def up(self):
        self.selected = abs((self.selected - 1) % len(self.options))

    def down(self):
        self.selected = abs((self.selected + 1) % len(self.options))

    def select(self):
        return self.options[self.selected]

    def prepare(self):
        self.toPrint = []
        for index, item in enumerate(self.options):
            if index == self.selected:
                menuItem, menuItemPos = write(item, self.fontSelected['size'], self.font, self.fontSelected['color'])
            else:
                menuItem, menuItemPos = write(item, self.fontDefault['size'], self.font, self.fontDefault['color'])
            self.toPrint.append((menuItem, menuItemPos))
        self.menuWidth = int(max([x[0].get_width() for x in self.toPrint]))
        self.menuHeight = int(sum([x[0].get_height() for x in self.toPrint]))
        print(self.menuWidth)
        print(self.menuHeight)

    def show(self):
        dispBy = 0
        for item in self.toPrint:
            if self.align == 'center':
                item[1].centerx = self.menuFrame.get_rect().centerx
            elif self.align == 'right':
                item[1].right = self.menuFrame.get_rect().right
            self.menuFrame.blit(item[0], (item[1].x, (item[1].y + dispBy)))
            dispBy += item[0].get_height()
        return self.menuFrame


menu = ListMenu()

count = 0
while count < 1600:
    print(count)
    background.blit(menu.show(), (0, 0))
    screen.blit(background, (0, 0))
    pygame.display.flip()
    count += 1