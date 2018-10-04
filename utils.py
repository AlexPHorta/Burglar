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

# from tools import loadConfigs


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

def blit_alpha(target, source, location, opacity):
    x = location[0]
    y = location[1]
    temp = pygame.Surface((source.get_width(), source.get_height())).convert()
    temp.blit(target, (-x, -y))
    temp.blit(source, (0, 0))
    temp.set_alpha(opacity)
    target.blit(temp, location)

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
        self.PURPLE = load_png('purple_stone.png')

stones = StoneColors()


class Colors:

    def __init__(self):
        self.light = {
            'mmbg': '#FEFDF6', 'mmtt': '#3F130F', 'mmna': '#193F4E', 'mmni': '#317588', \
            'opbg': '#FFFFFF', 'optt': '#AAAAAA', 'opmt': '#AAAAAA', 'opmna': '#AAAAAA', 'opmni': '#AAAAAA', \
            'gbgimg': 'bg_light.png', 'gbg': (246,175,108), 'gmn': '#AAAAAA', 'gmna': '#AAAAAA', \
            'gmni': '#AAAAAA', 'gmns': '#AAAAAA', 'gmno': '#AAAAAA', 'gmnw': '#AAAAAA', \
            'gsc': '#AAAAAA', 'ggo': '#AAAAAA'}

        self.dark = {
            'mmbg': '#AAAAAA', 'mmtt': '#AAAAAA', 'mmna': '#AAAAAA', 'mmni': '#AAAAAA', \
            'opbg': '#AAAAAA', 'optt': '#AAAAAA', 'opmt': '#AAAAAA', 'opmna': '#AAAAAA', 'opmni': '#AAAAAA', \
            'gbgimg': 'bg_light.png', 'gbg': (246,175,108), 'gmn': '#AAAAAA', 'gmna': '#AAAAAA', \
            'gmni': '#AAAAAA', 'gmns': '#AAAAAA', 'gmno': '#AAAAAA', 'gmnw': '#AAAAAA', \
            'gsc': '#AAAAAA', 'ggo': '#AAAAAA'}

        self.active = 'light'

    def setScheme(self, arg = 'light'):
        if arg == 'light':
            arg = self.light
            self.active = 'light'
        elif arg == 'dark':
            arg = self.dark
            self.active = 'dark'
        else:
            arg = self.light
            self.active = 'light'

        # Main menu color options
        self.MAINMENUBG =           toRGBA(arg['mmbg']  )
        self.MAINMENUTITLE =        toRGBA(arg['mmtt']  )
        self.MAINMENUACTIVE =       toRGBA(arg['mmna'] )
        self.MAINMENUINACTIVE =     toRGBA(arg['mmni'] )

        # Options screen color options
        self.OPTIONSBG =            toRGBA(arg['opbg']  )
        self.OPTIONSTITLE =         toRGBA(arg['optt']  )
        self.OPTMENUTAG =           toRGBA(arg['opmt'])
        self.OPTMENUACTIVE =        toRGBA(arg['opmna']  )
        self.OPTMENUINACTIVE =      toRGBA(arg['opmni']  )

        # Game color options
        self.GAMEBGIMAGE =          load_png(arg['gbgimg'])
        self.GAMEBG =               toRGBA(arg['gbg'] )
        self.GAMEMENU =             toRGBA(arg['gmn']  )
        self.GAMEMENUACTIVE =       toRGBA(arg['gmna'] )
        self.GAMEMENUINACTIVE =     toRGBA(arg['gmni'] )
        self.GAMEMENUSWITCHEDOFF =  toRGBA(arg['gmns'] )
        self.GAMEMENUOFF =          toRGBA(arg['gmno'] )
        self.GAMEMENUWARNING =      toRGBA(arg['gmnw'] )
        self.GAMESCORE =            toRGBA(arg['gsc']  )
        self.GAMEOVER =             toRGBA(arg['ggo']  )

    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['GAMEBGIMAGE']
        return state

    def __setstate__(self, state):
        # Restore instance attributes.
        self.__dict__.update(state)
        if self.active == 'light':
            self.GAMEBGIMAGE = load_png(self.light['gbgimg'])
        elif self.active == 'dark':
            self.GAMEBGIMAGE = load_png(self.dark['gbgimg'])
        else:
            self.GAMEBGIMAGE = load_png(self.light['gbgimg'])