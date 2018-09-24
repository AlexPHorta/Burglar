#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Burglar: a game of stones
#
# Copyright 2018 - Alexandre Paloschi Horta
# License: ???
#
# Website - http://www.buey.net.br/burglar


VERSION = "0.1"

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

import engine

from collections import namedtuple
from itertools import islice, chain


pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1, 1), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption('Burglar')

from utils import load_png, write, Center, stones, colorScheme

# class StoneColors:

#     def __init__(self):
#         self.blank = load_png('grid.png')
#         self.red = load_png('red_stone.png')
#         self.blue = load_png('blue_stone.png')
#         self.green = load_png('green_stone.png')
#         self.yellow = load_png('yellow_stone.png')
#         self.brown = load_png('brown_stone.png')


class Stone(pygame.sprite.Sprite):
    """A stone that sits still and just changes colors.
    Returns: stone object
    Functions: update
    Attributes: area"""

    def __init__(self, image = None, x = 0, y = 0, center = None, tag = None):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        if (x, y) == center:
            self.rect = self.image.get_rect(center = center)
        else:
            self.rect = self.image.get_rect(center = (center.x + x, center.y + y))
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()

    def updateImg(self, newStoneType = None):
        self.image = newStoneType


class Score:

    def __init__(self, font = None, size = 10, color = (0, 0, 0), bgcolor = (255, 255, 255)):
        fullname = os.path.join('fonts', font)
        self.font = pygame.font.Font(fullname, size)
        self.color = color
        self.bgcolor = bgcolor
        self.points = 0
        self.score = self.font.render(str(self.points), True, self.color, self.bgcolor)
        self.score = self.score.convert_alpha()
        self.scorepos = self.score.get_rect()

    def updateScore(self, newScore):
        self.points = newScore
        self.score = self.font.render(str(self.points), True, self.color, self.bgcolor)
        self.score = self.score.convert_alpha()
        self.scorepos = self.score.get_rect()
        return


class Game:

    gameKeys = {"left": 1, "right": 2}

    def __init__(self):
        self._running = True
        self.level = 'normal'
        self._display_surf = None
        self.size = self.width, self.height = 1350, 1000
        self.frameSize = self.frameWidth, self.frameHeight = 1100, 1000
        self.inner_ring = []
        self.middle_ring = []
        self.outer_ring = []
        self.big_outer_ring = []

        try:
            # pygame.mixer.music.load(os.path.join('data', 'an-turr.ogg'))#load music
            self.flip = pygame.mixer.Sound(os.path.join('sounds','167045__drminky__slime-jump.wav'))
            self.click = pygame.mixer.Sound(os.path.join('sounds','256116__kwahmah-02__click.wav'))
            self.toggle = pygame.mixer.Sound(os.path.join('sounds','202312__7778__dbl-click.wav'))
        except:
            raise UserWarning("could not load or play soundfiles in 'data' folder :-(")

    def on_init(self):

        self.screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill(colorScheme.BACKGROUND)
        self.gamebg = colorScheme.BGIMAGE
        self.mainMenu = True
        self.optionsScreen = False
        self.activeOption = 0
        self.menuGameActive = False
        self.gameOn = False
        self.gameOver = False
        self.pause = False
        self.option = 0

        from menus import ListMenu, SwitchableListMenu, FlattenedMenu

        self.mm = ListMenu(('easy', 'normal', 'hard', 'options', 'help'), sizes = (58, 63), align = 'center')
        self.gm = SwitchableListMenu(('pause', 'options', 'quit'), sizes = (52, 58, 52), align = 'right', bg = colorScheme.GAMEBG)
        self.rsm = ListMenu(('resume',), sizes = (52, 58), align = 'right', bg = colorScheme.GAMEBG)
        self.govm = ListMenu((('new game', self.level), 'back'), sizes = (52, 58), align = 'right', bg = colorScheme.GAMEBG)
        self.optm = FlattenedMenu(({'Theme': ('light', 'dark')}, {'Music': ('on', 'off')}, 'back'), sizes = (52, 58), align = 'center', bg = colorScheme.BACKGROUND)

    def menuMain(self):

        self.game = None

        # self.gameOn = False
        # self.mainMenu = True
        # self.optionsScreen = False

        # Print game name
        title, titlepos = write('Burglar', 124, 'Multicolore.otf', colorScheme.TITLE)
        titlepos.centerx, titlepos.centery = self.background.get_rect().center
        self.background.blit(title, titlepos)

        self.mm.assemble()
        self.mm.menuPos.top = titlepos.bottom + 100
        self.mm.menuPos.centerx = self.background.get_rect().centerx
        self.background.blit(self.mm.menu, self.mm.menuPos)

    def menuGame(self):

        bottommenupos = 920
        right = 1300

        if not self.gameOver:
            if not self.pause:
                self.gm.assemble()
                self.gm.menuPos.bottom = bottommenupos
                self.gm.menuPos.right = 1300
                self.background.blit(self.gm.menu, self.gm.menuPos)

                warning, warningpos = write('Press CTRL to toggle menu on/off.', 22, 'MankSans-Medium.ttf', colorScheme.MENUWARNING)

                # Print menu warning
                warningpos.right = right
                warningpos.bottom = 950
                self.background.blit(warning, warningpos)
            else:
                self.rsm.assemble()
                self.rsm.menuPos.bottom = bottommenupos
                self.rsm.menuPos.right = 1300
                self.background.blit(self.rsm.menu, self.rsm.menuPos)
        else:
            self.govm.options = (('new game', self.level), 'back') # Ugly, ugly, ugly!!!!!
            self.govm.assemble()
            self.govm.menuPos.bottom = bottommenupos
            self.govm.menuPos.right = 1300
            self.background.blit(self.govm.menu, self.govm.menuPos)


    def options(self):

        self.game = None

        # self.gameOn = False
        # self.mainMenu = False
        # self.optionsScreen = True

        # Print Options tag
        title, titlepos = write('Options', 82, 'Multicolore.otf', colorScheme.TITLE)
        titlepos.centerx = self.background.get_rect().centerx
        titlepos.top = 200
        self.background.blit(title, titlepos)

        self.optm.assemble()
        self.optm.menuPos.top = titlepos.bottom + 100
        self.optm.menuPos.centerx = self.background.get_rect().centerx
        self.background.blit(self.optm.menu, self.optm.menuPos)

    def load(self, option):
        option_ = str(option)
        # self.option = 0
        if option_ == 'easy':
            self.level = 'easy'
            self.loadGame()
        elif option_ == 'normal':
            self.level = 'normal'
            self.loadGame()
        elif option_ == 'hard':
            self.level = 'hard'
            self.loadGame()
        elif option_ == 'options':
            self.gameOn = False
            self.optionsScreen = True
            self.mainMenu = False
            self.gm.switch('off')
            # print('{} - {} - {}'.format(self.gameOn, self.optionsScreen, self.mainMenu))
            self.options()
        elif option_ == 'light':
            colorScheme.setScheme()
        elif option_ == 'dark':
            colorScheme.setScheme(1)
        elif option_ == 'help':
            pass
        elif option_ == 'pause':
            self.pause = True
        elif option_ == 'resume':
            self.pause = False
            self.gm.switch('off')
        elif option_ == 'quit' or option_ == 'back':
            self.gameOn = False
            self.optionsScreen = False
            self.mainMenu = True
            self.gm.switch('off')
            self.menuMain()

    def loadGame(self):

        self.gameOn = True
        self.mainMenu = False
        self.optionsScreen = False
        self.frame = pygame.Surface(self.frameSize)
        self.frameCENTER = Center(self.frame.get_rect().centerx, self.frame.get_rect().centery)

        self.inner_ring[:] = []
        self.middle_ring[:] = []
        self.outer_ring[:] = []
        self.big_outer_ring[:] = []
        self.inner_ring.append( Stone(image = stones.BLANK, x =  (math.sin(math.radians(45)) * 80),       y = -(math.cos(math.radians(45)) * 80),   center = self.frameCENTER, tag = "i0"))
        self.inner_ring.append( Stone(image = stones.BLANK, x =  (math.sin(math.radians(45)) * 80),       y =  (math.cos(math.radians(45)) * 80),  center = self.frameCENTER, tag = "i1"))
        self.inner_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(45)) * 80),       y =  (math.cos(math.radians(45)) * 80),  center = self.frameCENTER, tag = "i2"))
        self.inner_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(45)) * 80),       y = -(math.cos(math.radians(45)) * 80),   center = self.frameCENTER, tag = "i3"))

        self.middle_ring.append(Stone(image = stones.BLANK, x =  (math.sin(math.radians(22.5)) * 195),   y = -(math.cos(math.radians(22.5)) * 195),   center = self.frameCENTER, tag = "m0"))
        self.middle_ring.append(Stone(image = stones.BLANK, x =  (math.sin(math.radians(67.5)) * 195),   y = -(math.cos(math.radians(67.5)) * 195), center = self.frameCENTER, tag = "m1"))
        self.middle_ring.append(Stone(image = stones.BLANK, x =  (math.sin(math.radians(67.5)) * 195),    y = (math.cos(math.radians(67.5)) * 195),  center = self.frameCENTER, tag = "m2"))
        self.middle_ring.append(Stone(image = stones.BLANK, x =  (math.sin(math.radians(22.5)) * 195),    y = (math.cos(math.radians(22.5)) * 195),  center = self.frameCENTER, tag = "m3"))
        self.middle_ring.append(Stone(image = stones.BLANK, x = -(math.sin(math.radians(22.5)) * 195),    y = (math.cos(math.radians(22.5)) * 195),  center = self.frameCENTER, tag = "m4"))
        self.middle_ring.append(Stone(image = stones.BLANK, x = -(math.sin(math.radians(67.5)) * 195),    y = (math.cos(math.radians(67.5)) * 195),  center = self.frameCENTER, tag = "m5"))
        self.middle_ring.append(Stone(image = stones.BLANK, x = -(math.sin(math.radians(67.5)) * 195),   y = -(math.cos(math.radians(67.5)) * 195), center = self.frameCENTER, tag = "m6"))
        self.middle_ring.append(Stone(image = stones.BLANK, x = -(math.sin(math.radians(22.5)) * 195),   y = -(math.cos(math.radians(22.5)) * 195),   center = self.frameCENTER, tag = "m7"))

        self.outer_ring.append( Stone(image = stones.BLANK, x =  (math.sin(math.radians(11.25)) * 310),   y = -(math.cos(math.radians(11.25)) * 310),  center = self.frameCENTER, tag = "o0"))
        self.outer_ring.append( Stone(image = stones.BLANK, x =  (math.sin(math.radians(33.75)) * 310),   y = -(math.cos(math.radians(33.75)) * 310),  center = self.frameCENTER, tag = "o1"))
        self.outer_ring.append( Stone(image = stones.BLANK, x =  (math.sin(math.radians(56.25)) * 310),   y = -(math.cos(math.radians(56.25)) * 310), center = self.frameCENTER, tag = "o2"))
        self.outer_ring.append( Stone(image = stones.BLANK, x =  (math.sin(math.radians(78.75)) * 310),   y = -(math.cos(math.radians(78.75)) * 310), center = self.frameCENTER, tag = "o3"))
        self.outer_ring.append( Stone(image = stones.BLANK, x =  (math.sin(math.radians(78.75)) * 310),    y = (math.cos(math.radians(78.75)) * 310),  center = self.frameCENTER, tag = "o4"))
        self.outer_ring.append( Stone(image = stones.BLANK, x =  (math.sin(math.radians(56.25)) * 310),    y = (math.cos(math.radians(56.25)) * 310),  center = self.frameCENTER, tag = "o5"))
        self.outer_ring.append( Stone(image = stones.BLANK, x =  (math.sin(math.radians(33.75)) * 310),    y = (math.cos(math.radians(33.75)) * 310), center = self.frameCENTER, tag = "o6"))
        self.outer_ring.append( Stone(image = stones.BLANK, x =  (math.sin(math.radians(11.25)) * 310),    y = (math.cos(math.radians(11.25)) * 310), center = self.frameCENTER, tag = "o7"))
        self.outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(11.25)) * 310),   y =  (math.cos(math.radians(11.25)) * 310),  center = self.frameCENTER, tag = "o8"))
        self.outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(33.75)) * 310),   y =  (math.cos(math.radians(33.75)) * 310), center = self.frameCENTER, tag = "o9"))
        self.outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(56.25)) * 310),   y =  (math.cos(math.radians(56.25)) * 310), center = self.frameCENTER, tag = "o10"))
        self.outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(78.75)) * 310),   y =  (math.cos(math.radians(78.75)) * 310),  center = self.frameCENTER, tag = "o11"))
        self.outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(78.75)) * 310),  y = - (math.cos(math.radians(78.75)) * 310),   center = self.frameCENTER, tag = "o12"))
        self.outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(56.25)) * 310),  y = - (math.cos(math.radians(56.25)) * 310),  center = self.frameCENTER, tag = "o13"))
        self.outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(33.75)) * 310),  y = - (math.cos(math.radians(33.75)) * 310),  center = self.frameCENTER, tag = "o14"))
        self.outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(11.25)) * 310),  y = - (math.cos(math.radians(11.25)) * 310),   center = self.frameCENTER, tag = "o15"))

        self.big_outer_ring.append( Stone(image = stones.BLANK, x = (math.sin(math.radians(5.625)) *   430),   y = -(math.cos(math.radians(5.625)) *  430),  center = self.frameCENTER, tag = "b0"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = (math.sin(math.radians(16.875)) *  430),   y = -(math.cos(math.radians(16.875)) * 430),  center = self.frameCENTER, tag = "b1"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = (math.sin(math.radians(28.125)) *  430),   y = -(math.cos(math.radians(28.125)) * 430), center = self.frameCENTER, tag = "b2"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = (math.sin(math.radians(39.375)) *  430),   y = -(math.cos(math.radians(39.375)) * 430), center = self.frameCENTER, tag = "b3"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = (math.sin(math.radians(50.625)) *  430),   y = -(math.cos(math.radians(50.625)) * 430),  center = self.frameCENTER, tag = "b4"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = (math.sin(math.radians(61.875)) *  430),   y = -(math.cos(math.radians(61.875)) * 430),  center = self.frameCENTER, tag = "b5"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = (math.sin(math.radians(73.125)) *  430),   y = -(math.cos(math.radians(73.125)) * 430), center = self.frameCENTER, tag = "b6"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = (math.sin(math.radians(84.375)) *  430),   y = -(math.cos(math.radians(84.375)) * 430), center = self.frameCENTER, tag = "b7"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = (math.sin(math.radians(84.375)) *  430),    y = (math.cos(math.radians(84.375)) * 430), center = self.frameCENTER, tag = "b8"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = (math.sin(math.radians(73.125)) *  430),    y = (math.cos(math.radians(73.125)) * 430), center = self.frameCENTER, tag = "b9"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = (math.sin(math.radians(61.875)) *  430),    y = (math.cos(math.radians(61.875)) * 430),  center = self.frameCENTER, tag = "b10"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = (math.sin(math.radians(50.625)) *  430),    y = (math.cos(math.radians(50.625)) * 430),  center = self.frameCENTER, tag = "b11"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = (math.sin(math.radians(39.375)) *  430),    y = (math.cos(math.radians(39.375)) * 430), center = self.frameCENTER, tag = "b12"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = (math.sin(math.radians(28.125)) *  430),    y = (math.cos(math.radians(28.125)) * 430), center = self.frameCENTER, tag = "b13"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = (math.sin(math.radians(16.875)) *  430),    y = (math.cos(math.radians(16.875)) * 430),  center = self.frameCENTER, tag = "b14"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = (math.sin(math.radians(5.625)) *   430),     y = (math.cos(math.radians(5.625)) * 430),  center = self.frameCENTER, tag = "b15"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(5.625)) *  430),     y = (math.cos(math.radians(5.625)) * 430),  center = self.frameCENTER, tag = "b16"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(16.875)) * 430),    y = (math.cos(math.radians(16.875)) * 430),  center = self.frameCENTER, tag = "b17"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(28.125)) * 430),    y = (math.cos(math.radians(28.125)) * 430), center = self.frameCENTER, tag = "b18"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(39.375)) * 430),    y = (math.cos(math.radians(39.375)) * 430), center = self.frameCENTER, tag = "b19"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(50.625)) * 430),    y = (math.cos(math.radians(50.625)) * 430),  center = self.frameCENTER, tag = "b20"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(61.875)) * 430),    y = (math.cos(math.radians(61.875)) * 430),  center = self.frameCENTER, tag = "b21"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(73.125)) * 430),    y = (math.cos(math.radians(73.125)) * 430), center = self.frameCENTER, tag = "b22"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(84.375)) * 430),    y = (math.cos(math.radians(84.375)) * 430), center = self.frameCENTER, tag = "b23"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(84.375)) * 430),   y = -(math.cos(math.radians(84.375)) * 430), center = self.frameCENTER, tag = "b24"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(73.125)) * 430),   y = -(math.cos(math.radians(73.125)) * 430), center = self.frameCENTER, tag = "b25"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(61.875)) * 430),   y = -(math.cos(math.radians(61.875)) * 430),  center = self.frameCENTER, tag = "b26"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(50.625)) * 430),   y = -(math.cos(math.radians(50.625)) * 430),  center = self.frameCENTER, tag = "b27"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(39.375)) * 430),   y = -(math.cos(math.radians(39.375)) * 430), center = self.frameCENTER, tag = "b28"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(28.125)) * 430),   y = -(math.cos(math.radians(28.125)) * 430), center = self.frameCENTER, tag = "b29"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(16.875)) * 430),   y = -(math.cos(math.radians(16.875)) * 430),  center = self.frameCENTER, tag = "b30"))
        self.big_outer_ring.append( Stone(image = stones.BLANK, x = -(math.sin(math.radians(5.625)) *  430),    y = -(math.cos(math.radians(5.625)) * 430),  center = self.frameCENTER, tag = "b31"))

        if self.level == 'easy':
            self.game = engine.GameEngine_Easy()
        elif self.level == 'normal':
            self.game = engine.GameEngine_Normal()
        elif self.level == 'hard':
            self.game = engine.GameEngine_Hard()
        self.game.bag()
        self.game.insert_stone()

        self.fill_rings(self.game.outer, self.outer_ring)
        self.fill_rings(self.game.middle, self.middle_ring)
        self.fill_rings(self.game.inner, self.inner_ring)
        self.fill_rings(self.game.big_outer, self.big_outer_ring)

        self.score = Score('Multicolore.otf', 106, colorScheme.SCORE, colorScheme.GAMEBG)
        self.score.updateScore(self.game.points)

        self._running = True

    def on_event(self, event):

        # Check if user wants to drop the game (unlikely)
        if event.type == pygame.QUIT:
            self._running = False

        if self.mainMenu:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.mm.up()
                    self.flip.play()
                elif event.key == pygame.K_DOWN:
                    self.mm.down()
                    self.flip.play()
                elif event.key == pygame.K_RETURN:
                    self.click.play()
                    self.load(self.mm.select())

        if self.optionsScreen:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.optm.up()
                    self.flip.play()
                elif event.key == pygame.K_DOWN:
                    self.optm.down()
                    self.flip.play()
                if event.key == pygame.K_LEFT:
                    self.optm.left()
                elif event.key == pygame.K_RIGHT:
                    self.optm.right()
                elif event.key == pygame.K_RETURN:
                    self.click.play()
                    self.load(self.optm.select())

            # if self.option == 0:
            #     colorScheme.setScheme()
            # elif self.option == 1:
            #     colorScheme.setScheme(1)

        if self.gameOn:

            # Check if user pressed the right keys, turn things accordingly
            if event.type == pygame.KEYDOWN:

                if not (self.gameOver or self.pause):
                    if (event.key == pygame.K_LEFT) or (event.key == pygame.K_RIGHT):
                        self.game.where_to_turn(self.gameKeys[pygame.key.name(event.key)])
                        self.game.new_round()

                        if self.game.current_bag == []:
                            self.game.bag()

                        self.game.insert_stone()

                    elif (event.key == pygame.K_RCTRL) or (event.key == pygame.K_LCTRL):
                        if self.gm.switchedOn:
                            self.toggle.play()
                            self.gm.switch('off')
                        else:
                            self.toggle.play()
                            self.gm.switch('on')

                if self.gameOver:
                    if event.key == pygame.K_UP:
                        self.govm.up()
                        self.flip.play()
                    elif event.key == pygame.K_DOWN:
                        self.govm.down()
                        self.flip.play()
                    elif event.key == pygame.K_RETURN:
                        self.click.play()
                        self.load(self.govm.select())

                if self.pause:
                    if event.key == pygame.K_RETURN:
                        self.click.play()
                        self.load(self.rsm.select())

                if self.gm.switchedOn:
                    if event.key == pygame.K_UP:
                        self.gm.up()
                        self.flip.play()
                    elif event.key == pygame.K_DOWN:
                        self.gm.down()
                        self.flip.play()
                    elif event.key == pygame.K_RETURN:
                        self.click.play()
                        self.load(self.gm.select())


    def on_loop(self):

        # Slow down things a bit
        clock.tick(40)

        if self.gameOn:

            # Refresh the state of the rings
            self.fill_rings(self.game.big_outer, self.big_outer_ring)
            self.fill_rings(self.game.outer, self.outer_ring)
            self.fill_rings(self.game.middle, self.middle_ring)
            self.fill_rings(self.game.inner, self.inner_ring)

            # Refresh the score
            self.score.updateScore(self.game.points)

            self.gameOver = self.game.game_over

        return

    def on_render(self):
        # Empty screen
        self.screen.blit(self.background, (0, 0))

        if self.mainMenu:
            self.background.fill(colorScheme.BACKGROUND)
            self.menuMain()

        if self.optionsScreen:
            self.background.fill(colorScheme.BACKGROUND)
            self.options()

        elif self.gameOn:

            # self.background.fill(self.syscolors.BACKGROUND)
            self.background.blit(self.gamebg, (0, 0))

            # Blit score
            self.score.scorepos.right = 1300
            self.score.scorepos.top = 50 #self.background.get_rect().centery
            self.background.blit(self.score.score, self.score.scorepos)

            # Blit rings
            for ring in (self.big_outer_ring, self.outer_ring, self.middle_ring, self.inner_ring):
                for element in ring:
                    self.background.blit(element.image, element.rect)

            self.menuGame()

            # Blit game over
            if self.gameOver:
                gOver, gOverpos = write('Game Over', 124, 'Multicolore.otf', colorScheme.GAMEOVER)
                gOverpos.centerx, gOverpos.centery = self.frame.get_rect().center

                self.background.blit(gOver, gOverpos)

        self.screen.blit(self.background, (0, 0))

        # Refresh everything
        pygame.display.flip()
        return

    def on_cleanup(self):
        pygame.quit()
        return

    def on_execute(self):
        if self.on_init() == False:
            self._running = False
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

    def fill_rings(self, engine_ring, screen_ring):
        for indice, hole in enumerate(engine_ring):
            if engine_ring[indice] == 0:
                screen_ring[indice].updateImg(stones.BLANK)
            elif engine_ring[indice] == 1:
                screen_ring[indice].updateImg(stones.RED)
            elif engine_ring[indice] == 2:
                screen_ring[indice].updateImg(stones.BLUE)
            elif engine_ring[indice] == 3:
                screen_ring[indice].updateImg(stones.GREEN)
            elif engine_ring[indice] == 4:
                screen_ring[indice].updateImg(stones.YELLOW)
            elif engine_ring[indice] == 5:
                screen_ring[indice].updateImg(stones.BROWN)
            else:
                continue
        return


def main():

    game_ = Game()

    game_.on_execute()


if __name__ == '__main__': main()
