#!/usr/bin/env python
import getopt
import math
import os
import os.path
import pathlib
import random
import sys

try:
    import pygame
    from socket import *
    from pygame.locals import *
except ImportError as err:
    print(f"Couldn't load module. {err}")
    sys.exit(2)


pygame.mixer.pre_init(44100, -16, 2, 4096)
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = "True"
clock = pygame.time.Clock()
flags = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE | pygame.SCALED
info = pygame.display.get_desktop_sizes()
screenW = info[0][0]
screenH = info[0][1]
print(str(info))
screen = pygame.display.set_mode((1, 1), flags)
pygame.display.set_caption('Burglar')

ROOT_DIR = pathlib.Path(os.path.abspath(__file__)).parent

def main():
    from game import Game

    game_ = Game()

    game_.on_execute()


if __name__ == '__main__': main()
