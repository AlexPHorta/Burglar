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
from enum import Enum, unique
from itertools import islice, chain, cycle


pygame.mixer.pre_init(44100, -16, 2, 4096)
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1, 1), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption('Burglar')

from utils import load_png, blit_alpha, write, Center, stones
from tools import saveConfigs, colorScheme, configurations


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

    def surge(self):
        pass



class Score:

    def __init__(self, font = None, size = 10, color = (0, 0, 0), bgcolor = None):
        fullname = os.path.join('fonts', font)
        self.font = pygame.font.Font(fullname, size)
        self.color = color
        self.bgcolor = bgcolor
        self.points = 0
        if bgcolor:
            self.score = self.font.render(str(self.points), True, self.color, self.bgcolor)
        else:
            self.score = self.font.render(str(self.points), True, self.color)
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
        self.track = pygame.mixer.music

        try:
            self.track.load(os.path.join('sounds', '392395__shadydave__cello-marcato-loop.wav'))
            self.splashTrack = pygame.mixer.Sound(os.path.join('sounds', '270657__shadydave__deep-bass-growl.wav'))
            self.flip = pygame.mixer.Sound(os.path.join('sounds','167045__drminky__slime-jump.wav'))
            self.click = pygame.mixer.Sound(os.path.join('sounds','256116__kwahmah-02__click.wav'))
            self.toggle = pygame.mixer.Sound(os.path.join('sounds','202312__7778__dbl-click.wav'))
        except:
            raise UserWarning("could not load or play soundfiles in 'sounds' folder :-(")

        if configurations:
            self.music = configurations[1]
            self.sound = configurations[2]
        else:
            self.music = True
            self.sound = True

    def on_init(self):

        self.screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()

        self.splashScreen()

        self.background.fill(colorScheme.GAMEBG)
        self.gamebg = colorScheme.GAMEBGIMAGE
        self.activeScreen = 0
        self.mainMenu = True
        self.optionsScreen = False
        self.activeOption = 0
        self.menuGameActive = False
        self.gameOn = False
        self.gameOver = False
        self.pause = False
        self.help_ = 0

        from menus import ListMenu, SwitchableListMenu, FlattenedMenu

        self.mm = ListMenu(('easy', 'normal', 'hard', 'options', 'help', 'credits'), sizes = (58, 63), \
            bg = colorScheme.MAINMENUBG, mncolors = (colorScheme.MAINMENUINACTIVE, colorScheme.MAINMENUACTIVE), align = 'center')
        self.gm = SwitchableListMenu(('pause', 'quit'), sizes = (52, 58, 52), \
            mncolors = (colorScheme.GAMEMENUINACTIVE, colorScheme.GAMEMENUACTIVE), align = 'right')
        self.rsm = ListMenu(('resume',), sizes = (52, 58), mncolors = (colorScheme.GAMEMENUINACTIVE, colorScheme.GAMEMENUACTIVE), align = 'right')
        self.govm = ListMenu((('new game', self.level), 'back'), sizes = (52, 58), mncolors = (colorScheme.GAMEMENUINACTIVE, colorScheme.GAMEMENUACTIVE), align = 'right')
        self.optm = FlattenedMenu(({'Sound': ('on', 'off')}, {'Music': ('on', 'off')}, 'back'), \
            sizes = (52, 58), align = 'center', bg = colorScheme.OPTIONSBG, \
            mncolors = (colorScheme.OPTMENUINACTIVE, colorScheme.OPTMENUACTIVE), hpad = 20, vpad = 20)
        self.hm = ListMenu(('back',), sizes = (58, 63), mncolors = (colorScheme.OPTMENUINACTIVE, colorScheme.OPTMENUACTIVE), align = 'center')
        self.cm = ListMenu(('back',), sizes = (58, 63), mncolors = (colorScheme.OPTMENUINACTIVE, colorScheme.OPTMENUACTIVE), align = 'center')

    def splashScreen(self):
        self.background.fill((0, 0, 0))
        bg = load_png('splash_bg.png')

        self.background.blit(bg, (0, 0))

        self.splashTrack.play(1)

        for i in range(0, 255, 10):
            self.background.set_alpha(i)
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
            pygame.time.wait(10)

        buey_spritesheet = load_png('buey_sprite.png')
        buey_spritesheetPos = buey_spritesheet.get_rect()
        buey_spritesheetPos.centerx = self.background.get_rect().centerx
        buey_spritesheetPos.centery = self.background.get_rect().centery

        for i in range(0, 255, 4):
            self.background.blit(bg, (0, 0))
            blit_alpha(self.background, buey_spritesheet, buey_spritesheetPos, i)
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
            pygame.time.wait(10)

        pygame.time.wait(1500)

        fadeOut = pygame.Surface(self.screen.get_size())

        for i in range(0, 255, 10):
            self.background.blit(bg, (0, 0))
            self.background.blit(buey_spritesheet, buey_spritesheetPos)
            fadeOut.set_alpha(i)
            self.background.blit(fadeOut, (0, 0))
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
            pygame.time.wait(10)

        self.splashTrack.stop()

        pygame.time.wait(200)

    def menuMain(self):

        self.game = None

        # Print game name
        title, titlepos = write('Burglar', 124, 'Multicolore.otf', colorScheme.MAINMENUTITLE)
        titlepos.centerx = self.background.get_rect().centerx
        titlepos.centery = self.background.get_rect().height / 3
        self.background.blit(title, titlepos)

        self.mm.assemble()
        self.mm.menuPos.centery = 2 * (self.background.get_rect().height / 3)
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

                warning, warningpos = write('Press CTRL to toggle menu on/off.', 22, 'MankSans-Medium.ttf', colorScheme.GAMEMENUWARNING)

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

        # Print Options tag
        title, titlepos = write('Options', 96, 'Multicolore.otf', colorScheme.OPTIONSTITLE)
        titlepos.centerx = self.background.get_rect().centerx
        titlepos.centery = self.background.get_rect().height / 3
        self.background.blit(title, titlepos)

        self.optm.assemble()
        self.optm.menuPos.centerx = self.background.get_rect().centerx
        self.optm.menuPos.centery = 2 * (self.background.get_rect().height / 3)
        self.background.blit(self.optm.menu, self.optm.menuPos)

    def help(self):

        self.game = None
        helpFile = 'help0{}.png'.format(str(self.help_))

        # Print Title
        title, titlepos = write('Help', 96, 'Multicolore.otf', colorScheme.OPTIONSTITLE)
        titlepos.centerx = self.background.get_rect().centerx
        titlepos.centery = self.background.get_rect().height / 6
        self.background.blit(title, titlepos)

        helpImage = load_png(helpFile)
        helpImagePos = helpImage.get_rect()
        helpImagePos.centerx = self.background.get_rect().centerx
        helpImagePos.centery = self.background.get_rect().centery
        self.background.blit(helpImage, helpImagePos)

        self.hm.assemble()
        self.hm.menuPos.centerx = self.background.get_rect().centerx
        self.hm.menuPos.centery = 5 * (self.background.get_rect().height / 6)
        self.background.blit(self.hm.menu, self.hm.menuPos)

    def credits(self):

        self.game = None

        # Print Options tag
        title, titlepos = write('Credits', 96, 'Multicolore.otf', colorScheme.TITLE)
        titlepos.centerx = self.background.get_rect().centerx
        titlepos.centery = self.background.get_rect().height / 6
        self.background.blit(title, titlepos)

        helpImage = load_png('help01.png')
        helpImagePos = helpImage.get_rect()
        helpImagePos.centerx = self.background.get_rect().centerx
        helpImagePos.centery = self.background.get_rect().centery
        self.background.blit(helpImage, helpImagePos)

        self.cm.assemble()
        self.cm.menuPos.centerx = self.background.get_rect().centerx
        self.cm.menuPos.centery = 5 * (self.background.get_rect().height / 6)
        self.background.blit(self.cm.menu, self.cm.menuPos)

    def load(self, choice, option = None):
        choice = str(choice)
        option = str(option)
        if choice == 'easy':
            self.activeScreen = 2
            self.level = 'easy'
            self.loadGame()
        elif choice == 'normal':
            self.activeScreen = 2
            self.level = 'normal'
            self.loadGame()
        elif choice == 'hard':
            self.activeScreen = 2
            self.level = 'hard'
            self.loadGame()
        elif choice == 'options':
            self.activeScreen = 1
            self.gm.switch('off')
            self.options()
        elif choice == 'light':
            colorScheme.setScheme('light')
            # self.optm.assemble()
        elif choice == 'dark':
            colorScheme.setScheme('dark')
            # self.optm.assemble()
        elif choice == 'help':
            self.activeScreen = 3
            self.gm.switch('off')
            self.help()
        elif choice == 'credits':
            self.activeScreen = 4
            self.gm.switch('off')
            self.credits()
        elif choice == 'pause':
            self.pause = True
        elif choice == 'resume':
            self.pause = False
            self.gm.switch('off')
        elif choice == 'on':
            if option == 'music':
                self.music = True
                self.track.play(-1)
            elif option == 'sound':
                self.sound = True
        elif choice == 'off':
            if option == 'music':
                self.music = False
                self.track.stop()
            elif option == 'sound':
                self.sound = False
        elif choice == 'quit' or choice == 'back':
            self.activeScreen = 0
            self.gm.switch('off')
            self.menuMain()

    def loadGame(self):

        self.gameOver = False
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

        self.fill_rings(self.game.big_outer, self.big_outer_ring)
        self.fill_rings(self.game.outer, self.outer_ring)
        self.fill_rings(self.game.middle, self.middle_ring)
        self.fill_rings(self.game.inner, self.inner_ring)

        self.score = Score('Multicolore.otf', 106, colorScheme.GAMESCORE)
        self.score.updateScore(self.game.points)

        if self.music: self.track.play(-1)

        self._running = True

    def on_event(self, event):

        # Check if user wants to drop the game (unlikely)
        if event.type == pygame.QUIT:
            self._running = False

        if self.activeScreen == 0: #self.mainMenu:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.mm.up()
                    if self.sound: self.flip.play()
                elif event.key == pygame.K_DOWN:
                    self.mm.down()
                    if self.sound: self.flip.play()
                elif event.key == pygame.K_RETURN: # and self.keyDelay == 0:
                    if self.sound: self.click.play()
                    self.load(self.mm.select())

        elif self.activeScreen == 1: #self.optionsScreen:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.optm.up()
                    if self.sound: self.flip.play()
                elif event.key == pygame.K_DOWN:
                    self.optm.down()
                    if self.sound: self.flip.play()
                if event.key == pygame.K_LEFT:
                    self.optm.left()
                elif event.key == pygame.K_RIGHT:
                    self.optm.right()
                elif event.key == pygame.K_RETURN:
                    self.load(*self.optm.select())

        elif self.activeScreen == 2: #self.gameOn:

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
                            if self.sound: self.toggle.play()
                            self.gm.switch('off')
                        else:
                            if self.sound: self.toggle.play()
                            self.gm.switch('on')

                if self.gameOver:
                    if event.key == pygame.K_UP:
                        self.govm.up()
                        if self.sound: self.flip.play()
                    elif event.key == pygame.K_DOWN:
                        self.govm.down()
                        if self.sound: self.flip.play()
                    elif event.key == pygame.K_RETURN:
                        if self.sound: self.click.play()
                        self.load(self.govm.select())

                if self.pause:
                    if event.key == pygame.K_RETURN:
                        if self.sound: self.click.play()
                        self.load(self.rsm.select())

                if self.gm.switchedOn:
                    if event.key == pygame.K_UP:
                        self.gm.up()
                        if self.sound: self.flip.play()
                    elif event.key == pygame.K_DOWN:
                        self.gm.down()
                        if self.sound: self.flip.play()
                    elif event.key == pygame.K_RETURN:
                        if self.sound: self.click.play()
                        self.load(self.gm.select())

        elif self.activeScreen == 3:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_LEFT:
                    self.help_ = abs((self.help_ - 1) % 5)
                    if self.sound: self.flip.play()
                    self.load('help')
                elif event.key == pygame.K_RIGHT:
                    self.help_ = abs((self.help_ + 1) % 5)
                    if self.sound: self.flip.play()
                    self.load('help')
                elif event.key == pygame.K_RETURN:
                    if self.sound: self.click.play()
                    self.load(self.hm.select())

        elif self.activeScreen == 4:

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                        if self.sound: self.click.play()
                        self.load(self.cm.select())

    def on_loop(self):

        # Slow down things a bit
        clock.tick(20)

        if self.activeScreen == 2: #self.gameOn:

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

        if self.activeScreen == 0: #self.mainMenu:
            self.background.fill(colorScheme.MAINMENUBG)
            self.menuMain()

        elif self.activeScreen == 1: #self.optionsScreen:
            self.background.fill(colorScheme.OPTIONSBG)
            self.options()

        elif self.activeScreen == 2: #self.gameOn:

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
                gOverSemiTrans = load_png('game_over.png')
                gOverSemiTransPos = gOverSemiTrans.get_rect()
                gOverSemiTransPos.center = self.frameCENTER

                gOver, gOverpos = write('Game Over', 124, 'Multicolore.otf', colorScheme.GAMEOVER)
                gOverpos.centerx, gOverpos.centery = self.frame.get_rect().center

                self.background.blit(gOverSemiTrans, gOverSemiTransPos)

                self.background.blit(gOver, gOverpos)

        elif self.activeScreen == 3:

            self.background.fill(colorScheme.OPTIONSBG)
            self.help()

        elif self.activeScreen == 4:

            self.background.fill(colorScheme.OPTIONSBG)
            self.credits()

        self.screen.blit(self.background, (0, 0))

        # Refresh everything
        pygame.display.flip()
        return

    def on_cleanup(self):
        colorScheme.getScheme()
        confs = (colorScheme, self.music, self.sound)
        saveConfigs(confs)
        pygame.quit()
        return

    def on_execute(self):
        if self.on_init() == False:
            self._running = False
        while self._running:
            # for event in pygame.event.wait():
            #     self.on_event(event)
            # if pygame.event.peek((KEYDOWN, QUIT)):
            self.on_event(pygame.event.wait())
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
                screen_ring[indice].updateImg(stones.PURPLE)
            else:
                continue
        return


def main():

    game_ = Game()

    game_.on_execute()


if __name__ == '__main__': main()
