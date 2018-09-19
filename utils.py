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
        print ('Cannot load image: %s') % (fullname)
        raise (SystemExit, message)
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


class Colors:

    def __init__(self):
        self.BACKGROUND = (0, 7, 10)
        self.GAMEBG = (246,175,108)
        self.TITLE = (11, 181, 255)
        self.MENU = (76, 152, 193)
        self.MENUACTIVE = (37, 94, 118)
        self.MENUOFF = (245, 166, 92)
        self.SCORE = (9, 21, 26)
        self.MENUWARNING = (27, 65, 75)

colorScheme = Colors()