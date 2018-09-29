#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Burglar: a game of stones
#
# Copyright 2018 - Alexandre Paloschi Horta
# License: ???
#
# Website - http://www.buey.net.br/burglar

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
    print("Couldn't load module. %s") % (err)
    sys.exit(2)

from collections import namedtuple
from itertools import islice

from tools import loadConfigs


# The center of the screen. Makes it easier to place the stones.
Center = namedtuple('Center', 'x y')


# Some auxiliary functions
def load_png(name):
    """ Load image and return image object"""
    fullname = os.path.join('images', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error as message:
        print ('Cannot load image: {}'.format(fullname))
        raise SystemExit(message)
    return image

def write(text, size, font = None, color = (255, 255, 255)):
    if not font:
        font = pygame.font.SysFont('helvetica', size)
    else:
        fullname = os.path.join('fonts', font)
        font = pygame.font.Font(fullname, size)
    text = font.render(str(text), True, color)
    if text.get_alpha() is None:
        text = text.convert()
    else:
        text = text.convert_alpha()
    textpos = text.get_rect()
    return text, textpos

def toRGBA(color):
    if isinstance(color, tuple) and (len(color) == 3 or len(color) == 4):
        return color
    color = list(str(color))
    it = zip(islice(color, 1, len(color) - 1, 2), islice(color, 2, len(color), 2))
    if color[0] == '#':
        r = int(''.join(next(it)), base = 16)
        g = int(''.join(next(it)), base = 16)
        b = int(''.join(next(it)), base = 16)
        try:
            a = int(''.join(next(it)), base = 16)
            return (r, g, b, a)
        except StopIteration:
            return (r, g, b)


class StoneColors:

    def __init__(self):
        self.BLANK = load_png('grid.png')
        self.RED = load_png('red_stone.png')
        self.BLUE = load_png('blue_stone.png')
        self.GREEN = load_png('green_stone.png')
        self.YELLOW = load_png('yellow_stone.png')
        self.BROWN = load_png('brown_stone.png')

stones = StoneColors()


class Colors:

    def __init__(self):
        self.light = {'bgimg': 'bg_light.png', 'bg': '#F8C18D', 'gbg': (246,175,108), \
            'tt': (11, 181, 255), 'mn': (76, 152, 193), 'mna': (37, 94, 118), \
            'mni': (11, 26, 30), 'mns': '#F5A65C', 'mno': (245, 166, 92), 'omt': '#9C3025', 'sc': (9, 21, 26), \
            'mnw': (27, 65, 75), 'go': (251, 219, 189)}
        self.dark = {'bgimg': 'bg_light.png', 'bg': (0, 7, 10), 'gbg': (246,175,108), \
            'tt': (94, 29, 22), 'mn': (76, 152, 193), 'mna': (37, 94, 118), \
            'mni': (11, 26, 30), 'mns': (0, 0, 0), 'mno': (245, 166, 92), 'omt': '#9C3025', 'sc': (9, 21, 26), \
            'mnw': (27, 65, 75), 'go': (251, 219, 189)}
        self.setScheme()

    def setScheme(self, arg = None):
        if arg == None:
            arg = self.light
        else:
            arg = self.dark
        self.BGIMAGE = load_png(arg['bgimg'])
        self.BACKGROUND =           toRGBA(arg['bg']  )
        self.GAMEBG =               toRGBA(arg['gbg'] )
        self.TITLE =                toRGBA(arg['tt']  )
        self.MENU =                 toRGBA(arg['mn']  )
        self.MENUACTIVE =           toRGBA(arg['mna'] )
        self.MENUINACTIVE =         toRGBA(arg['mni'] )
        self.MENUSWITCHEDOFF =      toRGBA(arg['mns'] )
        self.MENUOFF =              toRGBA(arg['mno'] )
        self.OPTMENUTAG =           toRGBA(arg['omt'])
        self.SCORE =                toRGBA(arg['sc']  )
        self.MENUWARNING =          toRGBA(arg['mnw'] )
        self.GAMEOVER =             toRGBA(arg['go']  )

try:
    colorScheme = loadConfigs()
except:
    colorScheme = Colors()