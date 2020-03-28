#!/usr/bin/env python
# -*- encoding: utf-8 -*-

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

    def __init__(self,
        image = None,
        x = 0,
        y = 0,
        center = None,
        tag = None):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        if (x, y) == center:
            self.rect = self.image.get_rect(center = center)
        else:
            self.rect = self.image.get_rect(center = (center.x + x,
                center.y + y))
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()

    def updateImg(self, newStoneType = None):
        self.image = newStoneType

    def surge(self):
        pass



class Score:

    def __init__(self,
        font = None,
        size = 10,
        color = (0, 0, 0),
        bgcolor = None):
        fullname = os.path.join('fonts', font)
        self.font = pygame.font.Font(fullname, size)
        self.color = color
        self.bgcolor = bgcolor
        self.points = 0
        if bgcolor:
            self.score = self.font.render(
                str(self.points), True, self.color, self.bgcolor)
        else:
            self.score = self.font.render(str(self.points), True, self.color)
        self.score = self.score.convert_alpha()
        self.scorepos = self.score.get_rect()

    def updateScore(self, newScore):
        self.points = newScore
        self.score = self.font.render(
            str(self.points), True, self.color, self.bgcolor)
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
            self.track.load(os.path.join(
                'sounds', '392395__shadydave__cello-marcato-loop.wav'))
            self.splashTrack = pygame.mixer.Sound(os.path.join(
                'sounds', '270657__shadydave__deep-bass-growl.wav'))
            self.flip = pygame.mixer.Sound(os.path.join(
                'sounds','167045__drminky__slime-jump.wav'))
            self.click = pygame.mixer.Sound(os.path.join(
                'sounds','256116__kwahmah-02__click.wav'))
            self.toggle = pygame.mixer.Sound(os.path.join(
                'sounds','202312__7778__dbl-click.wav'))
            self.gOverSound = pygame.mixer.Sound(os.path.join(
                'sounds','145438__soughtaftersounds__old-music-box-5.wav'))
        except:
            raise UserWarning(
                "could not load or play soundfiles in 'sounds' folder :-(")

        if configurations:
            self.music = configurations[1]
            self.sound = configurations[2]
        else:
            self.music = True
            self.sound = True

    def on_init(self):

        self.screen = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
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

        from menus import (
            ListMenu,
            SwitchableListMenu,
            FlattenedMenu,
            CreditsTextBlock,
            )

        self.mm = ListMenu(
            ('easy', 'normal', 'hard', 'options', 'help', 'credits'),
            sizes = (58, 63),
            bg = colorScheme.MAINMENUBG,
            mncolors = (
                colorScheme.MAINMENUINACTIVE,
                colorScheme.MAINMENUACTIVE),
            align = 'center'
            )
        self.gm = SwitchableListMenu(
            ('pause', 'quit'),
            sizes = (52, 58, 52),
            mncolors = (
                colorScheme.GAMEMENUINACTIVE,
                colorScheme.GAMEMENUACTIVE),
            align = 'right',
            )
        self.rsm = ListMenu(
            ('resume',),
            sizes = (52, 58),
            mncolors = (
                colorScheme.GAMEMENUINACTIVE,
                colorScheme.GAMEMENUACTIVE),
            align = 'right',
            )
        self.govm = ListMenu(
            (('new game', self.level), 'back'),
            sizes = (52, 58),
            mncolors = (
                colorScheme.GAMEMENUINACTIVE,
                colorScheme.GAMEMENUACTIVE),
            align = 'right',
            )
        self.optm = FlattenedMenu(
            ({'Sound': ('on', 'off')}, {'Music': ('on', 'off')}, 'back'),
            sizes = (52, 58),
            align = 'center',
            bg = colorScheme.OPTIONSBG,
            mncolors = (
                colorScheme.OPTMENUINACTIVE,
                colorScheme.OPTMENUACTIVE),
            hpad = 20,
            vpad = 20,
            )
        self.hm = ListMenu(
            ('back',),
            sizes = (58, 63),
            mncolors = (
                colorScheme.OPTMENUINACTIVE,
                colorScheme.OPTMENUACTIVE),
            align = 'center',
            )

        creditsTexts = (
            ('Produced by', 'BUEY - Games and Stuff'),
            ('Programming, Testing, Artwork, Coffee', 'Alexandre Paloschi'),
            ('Website', 'www.buey.net.br'), ('Made with', 'Pygame'),
            ('Music', (
                'Marcato loop by Shady Dave',
                'https://www.freesound.org/people/ShadyDave/'))
            )
            # ('Sound Effects', ('https://freesound.org/people/DrMinky/sounds/167045/', '(https://creativecommons.org/licenses/by/3.0/)',
            #     'https://freesound.org/people/kwahmah_02/sounds/256116/', '(https://creativecommons.org/publicdomain/zero/1.0/)',
            #     'https://freesound.org/people/7778/sounds/202312/', '(https://creativecommons.org/publicdomain/zero/1.0/)',
            #     'https://freesound.org/people/ShadyDave/sounds/270657/', '(https://creativecommons.org/licenses/by/3.0/)')))

        self.credits_ = CreditsTextBlock(
            creditsTexts,
            sizes = (26, 26),
            align = 'center',
            bg = colorScheme.OPTIONSBG,
            mncolors = (
                colorScheme.OPTMENUINACTIVE,
                colorScheme.OPTMENUACTIVE),
            hpad = 20,
            vpad = 10,
            )
        self.cm = ListMenu(
            ('back',),
            sizes = (58, 63),
            mncolors = (
                colorScheme.OPTMENUINACTIVE,
                colorScheme.OPTMENUACTIVE),
            align = 'center',
            )

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

                warning, warningpos = write(
                    'Press CTRL to toggle menu on/off.', 22,
                    'MankSans-Medium.ttf',
                    colorScheme.GAMEMENUWARNING)

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
        title, titlepos = write(
            'Options', 96,
            'Multicolore.otf',
            colorScheme.OPTIONSTITLE,
            )
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
        title, titlepos = write(
            'Help', 96,
            'Multicolore.otf',
            colorScheme.OPTIONSTITLE,
            )
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
        title, titlepos = write(
            'Credits', 96,
            'Multicolore.otf',
            colorScheme.OPTIONSTITLE,
            )
        titlepos.centerx = self.background.get_rect().centerx
        titlepos.centery = self.background.get_rect().height / 8
        self.background.blit(title, titlepos)

        self.credits_.assemble()
        self.credits_.menuPos.centerx = self.background.get_rect().centerx
        self.credits_.menuPos.centery = self.background.get_rect().centery
        self.background.blit(self.credits_.menu, self.credits_.menuPos)

        self.cm.assemble()
        self.cm.menuPos.centerx = self.background.get_rect().centerx
        self.cm.menuPos.centery = 7 * (self.background.get_rect().height / 8)
        self.background.blit(self.cm.menu, self.cm.menuPos)

    def load(self, choice, option = None):
        levels = ('easy', 'normal', 'hard',)
        secondaries = {'options': 1, 'help': 3, 'credits': 4, 'quit': 0, 'back': 0,}
        choice = str(choice)
        option = str(option)
        if choice in levels:
            self.activeScreen = 2
            self.level = choice
            self.loadGame()
        elif choice in secondaries:
            self.activeScreen = secondaries[choice]
            self.gm.switch('off')
            if choice not in ('quit', 'back'):
                getattr(self, choice)()
            else:
                self.menuMain()
        elif choice in ('light', 'dark'):
            colorScheme.setScheme(choice)
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

    def loadGame(self):

        self.gameOver = False
        self.frame = pygame.Surface(self.frameSize)
        self.frameCENTER = Center(
            self.frame.get_rect().centerx, self.frame.get_rect().centery)

        self.inner_ring.clear()
        self.middle_ring.clear()
        self.outer_ring.clear()
        self.big_outer_ring.clear()
        coords = (
            ("inner_ring", 80, (
                (45, 1, 45, -1, "i0"), (45, 1, 45, 1, "i1"),
                (45, -1, 45, 1, "i2"), (45, -1, 45, -1, "i3"),
                )),
            ("middle_ring", 195, (
                (22.5, 1,  22.5, -1, "m0"), (67.5, 1,  67.5, -1,  "m1"),
                (67.5, 1, 67.5, 1,  "m2"), (22.5, 1, 22.5, 1, "m3"),
                (22.5, -1,  22.5, 1, "m4"), (67.5, -1,  67.5, 1,  "m5"),
                (67.5, -1, 67.5, -1,  "m6"), (22.5, -1, 22.5, -1, "m7"),
                )),
            ("outer_ring", 310, (
                (11.25, 1,  11.25, -1, "o0"), (33.75, 1,  33.75, -1,  "o1"),
                (56.25, 1, 56.25, -1,  "o2"), (78.75, 1, 78.75, -1, "o3"),
                (78.75, 1,  78.75, 1, "o4"), (56.25, 1,  56.25, 1,  "o5"),
                (33.75, 1, 33.75, 1,  "o6"), (11.25, 1, 11.25, 1, "o7"),
                (11.25, -1,  11.25, 1, "o8"), (33.75, -1,  33.75, 1,  "o9"),
                (56.25, -1, 56.25, 1,  "o10"), (78.75, -1, 78.75, 1, "o11"),
                (78.75, -1,  78.75, -1, "o12"), (56.25, -1,  56.25, -1,  "o13"),
                (33.75, -1, 33.75, -1,  "o14"), (11.25, -1, 11.25, -1, "o16"),
                )),
            ("big_outer_ring", 430, (
                (5.625, 1,  5.625, -1, "b0"), (16.875, 1,  16.875, -1,  "b1"),
                (28.125, 1, 28.125, -1,  "b2"), (39.375, 1, 39.375, -1, "b3"),
                (50.625, 1,  50.625, -1, "b4"), (61.875, 1,  61.875, -1,  "b5"),
                (73.125, 1, 73.125, -1,  "b6"), (84.375, 1, 84.375, -1, "b7"),
                (84.375, 1,  84.375, 1, "b8"), (73.125, 1,  73.125, 1,  "b9"),
                (61.875, 1, 61.875, 1,  "b10"), (50.625, 1, 50.625, 1, "b11"),
                (39.375, 1,  39.375, 1, "b12"), (28.125, 1,  28.125, 1,  "b13"),
                (16.875, 1, 16.875, 1,  "b14"), (5.625, 1, 5.625, 1, "b16"),
                (5.625, -1,  5.625, 1, "b17"), (16.875, -1,  16.875, 1,  "b18"),
                (28.125, -1, 28.125, 1,  "b19"), (39.375, -1, 39.375, 1, "b20"),
                (50.625, -1,  50.625, 1, "b21"), (61.875, -1,  61.875, 1,  "b22"),
                (73.125, -1, 73.125, 1,  "b23"), (84.375, -1, 84.375, 1, "b24"),
                (84.375, -1,  84.375, -1, "b25"), (73.125, -1,  73.125, -1,  "b26"),
                (61.875, -1, 61.875, -1,  "b27"), (50.625, -1, 50.625, -1, "b28"),
                (39.375, -1,  39.375, -1, "b29"), (28.125, -1,  28.125, -1,  "b30"),
                (16.875, -1, 16.875, -1,  "b31"), (5.625, -1, 5.625, -1, "b32"),
                )),
        )

        for index, coord in enumerate(coords):
            ring = getattr(self, coords[index][0])
            for coordx , multx, coordy, multy, tagg in coords[index][2]:
                ring.append(Stone(
                    image = stones.BLANK,
                    x = multx*(
                        math.sin(math.radians(coordx)) * coords[index][1]),
                    y = multy*(
                        math.cos(math.radians(coordy)) * coords[index][1]),
                    center = self.frameCENTER,
                    tag = tagg))

        levels = {
            'easy': engine.GameEngine_Easy,
            'normal': engine.GameEngine_Normal,
            'hard': engine.GameEngine_Hard
        }
        self.game = levels[self.level]()

        self.game.insert_stone()

        self.fill_rings(self.game.big_outer, self.big_outer_ring)
        self.fill_rings(self.game.outer, self.outer_ring)
        self.fill_rings(self.game.middle, self.middle_ring)
        self.fill_rings(self.game.inner, self.inner_ring)

        self.score = Score('Multicolore.otf', 106, colorScheme.GAMESCORE)
        self.score.updateScore(self.game.points)

        if self.music:
            self.track.play(-1)
            self.gOverSoundPlayed = False

        self._running = True

    def on_event(self, event):

        # Check if user wants to drop the game (unlikely)
        if event.type == pygame.QUIT:
            self._running = False

        keys = {
            pygame.K_UP: ('up', 'flip'),
            pygame.K_DOWN: ('down', 'flip'),
            pygame.K_LEFT: ('left', 'click'),
            pygame.K_RIGHT: ('right', 'click'),
            pygame.K_RETURN: ('select', 'click'),
        }

        def main_menu(event_, screen = self.mm):
            opt_ = getattr(screen, keys[event_.key][0])
            snd = getattr(self, keys[event_.key][1])
            if self.sound: snd.play()
            if event_.key != pygame.K_RETURN:
                opt_()
            else:
                if screen == self.mm:
                    self.load(opt_())
                elif screen == self.optm:
                    self.load(*opt_())

        def options_screen(event_):
            main_menu(event_, screen = self.optm)

        def game_on(event_):
            # Check if user pressed the right keys, turn things accordingly
            if not (self.gameOver or self.pause):
                if (event_.key == pygame.K_LEFT) or (event_.key == pygame.K_RIGHT):
                    self.game.where_to_turn(self.gameKeys[pygame.key.name(event_.key)])
                    self.game.new_round()

                    self.game.insert_stone()

                elif event_.key in (pygame.K_RCTRL, pygame.K_LCTRL):
                    if self.gm.switchedOn:
                        if self.sound: self.toggle.play()
                        self.gm.switch('off')
                    else:
                        if self.sound: self.toggle.play()
                        self.gm.switch('on')

            if self.gameOver:
                if event_.key == pygame.K_UP:
                    self.govm.up()
                    if self.sound: self.flip.play()
                elif event_.key == pygame.K_DOWN:
                    self.govm.down()
                    if self.sound: self.flip.play()
                elif event_.key == pygame.K_RETURN:
                    if self.sound: self.click.play()
                    self.load(self.govm.select())

            if self.pause:
                if event_.key == pygame.K_RETURN:
                    if self.sound: self.click.play()
                    self.load(self.rsm.select())

            if self.gm.switchedOn:
                if event_.key == pygame.K_UP:
                    self.gm.up()
                    if self.sound: self.flip.play()
                elif event_.key == pygame.K_DOWN:
                    self.gm.down()
                    if self.sound: self.flip.play()
                elif event_.key == pygame.K_RETURN:
                    if self.sound: self.click.play()
                    self.load(self.gm.select())

        def help_screen(event_):
            if event_.key == pygame.K_LEFT:
                self.help_ = abs((self.help_ - 1) % 6)
                if self.sound: self.flip.play()
                self.load('help')
            elif event_.key == pygame.K_RIGHT:
                self.help_ = abs((self.help_ + 1) % 6)
                if self.sound: self.flip.play()
                self.load('help')
            elif event_.key == pygame.K_RETURN:
                if self.sound: self.click.play()
                self.load(self.hm.select())

        def credits_screen(event_):
            if event_.key == pygame.K_RETURN:
                    if self.sound: self.click.play()
                    self.load(self.cm.select())

        screens = {
            0: main_menu,
            1: options_screen,
            2: game_on,
            3: help_screen,
            4: credits_screen,
        }

        if event.type == pygame.KEYDOWN:
            screens[self.activeScreen](event)

        return

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

            if self.gameOver:
                self.track.stop()

                if not self.gOverSoundPlayed:
                    self.gOverSound.play()
                    self.gOverSoundPlayed = True

        return

    def on_render(self):
        # Empty the screen
        self.screen.blit(self.background, (0, 0))

        def main_menu():
        # if self.activeScreen == 0: #self.mainMenu:
            self.background.fill(colorScheme.MAINMENUBG)
            self.menuMain()

        def options_screen():
        # elif self.activeScreen == 1: #self.optionsScreen:
            self.background.fill(colorScheme.OPTIONSBG)
            self.options()

        def game_on():
        # elif self.activeScreen == 2: #self.gameOn:

            # self.background.fill(self.syscolors.BACKGROUND)
            self.background.blit(self.gamebg, (0, 0))

            # Blit score
            self.score.scorepos.right = 1300
            self.score.scorepos.top = 50
            self.background.blit(self.score.score, self.score.scorepos)

            # Blit rings
            for ring in (
                self.big_outer_ring,
                self.outer_ring,
                self.middle_ring,
                self.inner_ring,
                ):
                for element in ring:
                    self.background.blit(element.image, element.rect)

            self.menuGame()

            # Blit game over
            if self.gameOver:
                gOverSemiTrans = load_png('game_over.png')
                gOverSemiTransPos = gOverSemiTrans.get_rect()
                gOverSemiTransPos.center = self.frameCENTER

                gOver, gOverpos = write(
                    'Game Over', 124,
                    'Multicolore.otf',
                    colorScheme.GAMEOVER,
                    )
                gOverpos.centerx, gOverpos.centery = self.frame.get_rect().center

                self.background.blit(gOverSemiTrans, gOverSemiTransPos)

                self.background.blit(gOver, gOverpos)

        def help_screen():
        # elif self.activeScreen == 3:

            self.background.fill(colorScheme.OPTIONSBG)
            self.help()

        def credits_screen():
        # elif self.activeScreen == 4:

            self.background.fill(colorScheme.OPTIONSBG)
            self.credits()

        screens = {
            0: main_menu,
            1: options_screen,
            2: game_on,
            3: help_screen,
            4: credits_screen,
        }

        screens[self.activeScreen]()

        self.screen.blit(self.background, (0, 0))

        # Refresh everything
        pygame.display.flip()
        return

    def on_cleanup(self):
        confs = (colorScheme, self.music, self.sound)
        saveConfigs(confs)
        pygame.quit()
        return

    def on_execute(self):
        if self.on_init() == False:
            self._running = False
        while self._running:
            self.on_event(pygame.event.wait())
            self.on_loop()
            self.on_render()
        self.on_cleanup()

    def fill_rings(self, engine_ring, screen_ring):
        stones_ = {
            0: stones.BLANK,
            1: stones.RED,
            2: stones.BLUE,
            3: stones.GREEN,
            4: stones.YELLOW,
            5: stones.PURPLE,}
        for index, hole in enumerate(engine_ring):
            screen_ring[index].updateImg(stones_[hole])
        return


def main():

    game_ = Game()

    game_.on_execute()


if __name__ == '__main__': main()
