#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Burglar: a game of stones
#
# Copyright 2018 - Alexandre Paloschi Horta
# License: ???
#
# Website - http://www.buey.net.br/burglar

XXX

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
except (ImportError, err):
    print("Couldn't load module. %s") % (err)
    sys.exit(2)

import engine

from collections import namedtuple

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1, 1), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption('Burglar')

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
    except (pygame.error, message):
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


class StoneColors:

    def __init__(self):
        self.blank = load_png('grid.png')
        self.red = load_png('red_stone.png')
        self.blue = load_png('blue_stone.png')
        self.green = load_png('green_stone.png')
        self.yellow = load_png('yellow_stone.png')
        self.brown = load_png('brown_stone.png')


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

    def __init__(self, font = None, size = 10):
        fullname = os.path.join('fonts', font)
        self.font = pygame.font.Font(fullname, size)
        self.points = 0
        self.score = self.font.render(str(self.points), True, (255, 255, 255), (5, 5, 5))
        self.score = self.score.convert_alpha()
        self.scorepos = self.score.get_rect()

    def updateScore(self, newScore):
        self.points = newScore
        self.score = self.font.render(str(self.points), True, (255, 255, 255), (5, 5, 5))
        self.score = self.score.convert_alpha()
        self.scorepos = self.score.get_rect()
        return


class Game:

    stoneTypes = StoneColors()

    BLANK = stoneTypes.blank
    RED = stoneTypes.red
    BLUE = stoneTypes.blue
    GREEN = stoneTypes.green
    YELLOW = stoneTypes.yellow
    BROWN = stoneTypes.brown

    gameKeys = {"left": 1, "right": 2}

    def __init__(self, level = 'normal'):
        self._running = True
        self.level = str(level)
        self._display_surf = None
        self.size = self.width, self.height = 1500, 1000
        self.frameSize = self.frameWidth, self.frameHeight = 1100, 1000
        self.inner_ring = []
        self.middle_ring = []
        self.outer_ring = []

    def on_init(self):

        self.screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((5, 5, 5))
        self.mainMenu = True
        self.menuGameActive = False
        self.gameOn = False
        self.pause = False
        self.option = 1

    def menuMain(self):

        self.game = None

        self.gameOn = False
        self.mainMenu = True

        # Print game name
        title, titlepos = write('Burglar', 124, 'Multicolore.otf')
        titlepos.centerx, titlepos.centery = self.background.get_rect().center
        self.background.blit(title, titlepos)

        self.menuOptions = ('easy', 'normal', 'hard', 'options', 'help')
        color = []
        topmenupos = 150
        topmenufsize = 56

        for index, item in enumerate(self.menuOptions):
            if index == self.option:
                color.append((255, 255, 0))
            else:
                color.append((255, 255, 255))

        easy, easypos = write('easy', topmenufsize, 'Multicolore.otf', color[0])
        normal, normalpos = write('normal', topmenufsize, 'Multicolore.otf', color[1])
        hard, hardpos = write('hard', topmenufsize, 'Multicolore.otf', color[2])
        options, optionspos = write('options', topmenufsize, 'Multicolore.otf', color[3])
        help_, help_pos = write('help', topmenufsize, 'Multicolore.otf', color[4])

        # Print easy option
        easypos.centerx = self.background.get_rect().centerx
        easypos.centery = self.background.get_rect().centery + topmenupos
        self.background.blit(easy, easypos)

        # Print normal option
        normalpos.centerx = self.background.get_rect().centerx
        normalpos.centery = self.background.get_rect().centery + topmenupos + topmenufsize
        self.background.blit(normal, normalpos)

        # Print hard option
        hardpos.centerx = self.background.get_rect().centerx
        hardpos.centery = self.background.get_rect().centery + topmenupos + (topmenufsize * 2)
        self.background.blit(hard, hardpos)

        # Print options option
        optionspos.centerx = self.background.get_rect().centerx
        optionspos.centery = self.background.get_rect().centery + topmenupos + (topmenufsize * 3)
        self.background.blit(options, optionspos)

        # Print help option
        help_pos.centerx = self.background.get_rect().centerx
        help_pos.centery = self.background.get_rect().centery + topmenupos + (topmenufsize * 4)
        self.background.blit(help_, help_pos)

    def menuGame(self):

        color = []
        topmenupos = 200
        topmenufsize = 56

        if self.pause:
            self.menuOptions = ('resume',)

            resume, resumepos = write('resume', topmenufsize, 'Multicolore.otf', (255, 255, 0))

            # Print resume option
            resumepos.right = 1400
            resumepos.centery = self.background.get_rect().centery + topmenupos
            self.background.blit(resume, resumepos)

        elif self.game.game_over:
            newGameoption = self.level
            self.menuOptions = (newGameoption, 'back')

            for index, item in enumerate(self.menuOptions):
                if index == self.option:
                    color.append((255, 255, 0))
                else:
                    color.append((255, 255, 255))

            newGame, newGamepos = write('new game', topmenufsize, 'Multicolore.otf', color[0])
            back, backpos = write('main menu', topmenufsize, 'Multicolore.otf', color[1])

            # Print new game option
            newGamepos.right = 1400
            newGamepos.centery = self.background.get_rect().centery + topmenupos
            self.background.blit(newGame, newGamepos)

            # Print back option
            backpos.right = 1400
            backpos.centery = self.background.get_rect().centery + topmenupos + (topmenufsize * 1)
            self.background.blit(back, backpos)

        else:
            self.menuOptions = ('pause', 'options', 'quit')

            if self.menuGameActive:
                for index, item in enumerate(self.menuOptions):
                    if index == self.option:
                        color.append((255, 255, 0))
                    else:
                        color.append((255, 255, 255))
            else:
                for index, item in enumerate(self.menuOptions):
                    color.append((10, 10, 10))

            pause, pausepos = write('pause', topmenufsize, 'Multicolore.otf', color[0])
            options, optionspos = write('options', topmenufsize, 'Multicolore.otf', color[1])
            quit, quitpos = write('quit', topmenufsize, 'Multicolore.otf', color[2])
            warning, warningpos = write('Press CTRL to toggle menu on/off.', 18, None, (255, 255, 255))

            # Print pause option
            pausepos.right = 1400
            pausepos.centery = self.background.get_rect().centery + topmenupos
            self.background.blit(pause, pausepos)

            # Print options option
            optionspos.right = 1400
            optionspos.centery = self.background.get_rect().centery + topmenupos + (topmenufsize * 1)
            self.background.blit(options, optionspos)

            # Print quit option
            quitpos.right = 1400
            quitpos.centery = self.background.get_rect().centery + topmenupos + (topmenufsize * 2)
            self.background.blit(quit, quitpos)

            # Print menu warning
            warningpos.right = 1400
            warningpos.bottom = 946
            self.background.blit(warning, warningpos)

    def load(self, option):
        option_ = str(option)
        if option_ == 'easy':
            self.option = 1
            self.level = 'easy'
            self.loadGame()
        elif option_ == 'normal':
            self.option = 1
            self.level = 'normal'
            self.loadGame()
        elif option_ == 'hard':
            self.option = 1
            self.level = 'hard'
            self.loadGame()
        elif option_ == 'options':
            pass
        elif option_ == 'help':
            pass
        elif option_ == 'pause':
            self.pause = True
        elif option_ == 'resume':
            self.pause = False
            self.menuGameActive = False
        elif option_ == 'quit' or option_ == 'back':
            self.option = 1
            self.menuGameActive = False
            self.menuMain()

    def loadGame(self):

        self.gameOn = True
        self.mainMenu = False
        self.frame = pygame.Surface(self.frameSize)
        self.frameCENTER = Center(self.frame.get_rect().centerx, self.frame.get_rect().centery)

        self.inner_ring[:] = []
        self.middle_ring[:] = []
        self.outer_ring[:] = []
        self.inner_ring.append( Stone(image = self.BLANK, x =  (math.sin(math.radians(45)) * 100),       y = -(math.cos(math.radians(45)) * 100),   center = self.frameCENTER, tag = "i0"))
        self.inner_ring.append( Stone(image = self.BLANK, x =  (math.sin(math.radians(45)) * 100),       y =  (math.cos(math.radians(45)) * 100),  center = self.frameCENTER, tag = "i1"))
        self.inner_ring.append( Stone(image = self.BLANK, x = -(math.sin(math.radians(45)) * 100),       y =  (math.cos(math.radians(45)) * 100),  center = self.frameCENTER, tag = "i2"))
        self.inner_ring.append( Stone(image = self.BLANK, x = -(math.sin(math.radians(45)) * 100),       y = -(math.cos(math.radians(45)) * 100),   center = self.frameCENTER, tag = "i3"))
        self.middle_ring.append(Stone(image = self.BLANK, x =  (math.sin(math.radians(22.5)) * 250),   y = -(math.cos(math.radians(22.5)) * 250),   center = self.frameCENTER, tag = "m0"))
        self.middle_ring.append(Stone(image = self.BLANK, x =  (math.sin(math.radians(67.5)) * 250),   y = -(math.cos(math.radians(67.5)) * 250), center = self.frameCENTER, tag = "m1"))
        self.middle_ring.append(Stone(image = self.BLANK, x =  (math.sin(math.radians(67.5)) * 250),    y = (math.cos(math.radians(67.5)) * 250),  center = self.frameCENTER, tag = "m2"))
        self.middle_ring.append(Stone(image = self.BLANK, x =  (math.sin(math.radians(22.5)) * 250),    y = (math.cos(math.radians(22.5)) * 250),  center = self.frameCENTER, tag = "m3"))
        self.middle_ring.append(Stone(image = self.BLANK, x = -(math.sin(math.radians(22.5)) * 250),    y = (math.cos(math.radians(22.5)) * 250),  center = self.frameCENTER, tag = "m4"))
        self.middle_ring.append(Stone(image = self.BLANK, x = -(math.sin(math.radians(67.5)) * 250),    y = (math.cos(math.radians(67.5)) * 250),  center = self.frameCENTER, tag = "m5"))
        self.middle_ring.append(Stone(image = self.BLANK, x = -(math.sin(math.radians(67.5)) * 250),   y = -(math.cos(math.radians(67.5)) * 250), center = self.frameCENTER, tag = "m6"))
        self.middle_ring.append(Stone(image = self.BLANK, x = -(math.sin(math.radians(22.5)) * 250),   y = -(math.cos(math.radians(22.5)) * 250),   center = self.frameCENTER, tag = "m7"))
        self.outer_ring.append( Stone(image = self.BLANK, x = (math.sin(math.radians(11.25)) * 400),   y = -(math.cos(math.radians(11.25)) * 400),  center = self.frameCENTER, tag = "o0"))
        self.outer_ring.append( Stone(image = self.BLANK, x = (math.sin(math.radians(33.75)) * 400),   y = -(math.cos(math.radians(33.75)) * 400),  center = self.frameCENTER, tag = "o1"))
        self.outer_ring.append( Stone(image = self.BLANK, x = (math.sin(math.radians(56.25)) * 400),   y = -(math.cos(math.radians(56.25)) * 400), center = self.frameCENTER, tag = "o2"))
        self.outer_ring.append( Stone(image = self.BLANK, x = (math.sin(math.radians(78.75)) * 400),   y = -(math.cos(math.radians(78.75)) * 400), center = self.frameCENTER, tag = "o3"))
        self.outer_ring.append( Stone(image = self.BLANK, x = (math.sin(math.radians(78.75)) * 400),    y = (math.cos(math.radians(78.75)) * 400),  center = self.frameCENTER, tag = "o4"))
        self.outer_ring.append( Stone(image = self.BLANK, x = (math.sin(math.radians(56.25)) * 400),    y = (math.cos(math.radians(56.25)) * 400),  center = self.frameCENTER, tag = "o5"))
        self.outer_ring.append( Stone(image = self.BLANK, x = (math.sin(math.radians(33.75)) * 400),    y = (math.cos(math.radians(33.75)) * 400), center = self.frameCENTER, tag = "o6"))
        self.outer_ring.append( Stone(image = self.BLANK, x = (math.sin(math.radians(11.25)) * 400),    y = (math.cos(math.radians(11.25)) * 400), center = self.frameCENTER, tag = "o7"))
        self.outer_ring.append( Stone(image = self.BLANK, x = -(math.sin(math.radians(11.25)) * 400),   y = (math.cos(math.radians(11.25)) * 400),  center = self.frameCENTER, tag = "o8"))
        self.outer_ring.append( Stone(image = self.BLANK, x = -(math.sin(math.radians(33.75)) * 400),   y = (math.cos(math.radians(33.75)) * 400), center = self.frameCENTER, tag = "o9"))
        self.outer_ring.append( Stone(image = self.BLANK, x = -(math.sin(math.radians(56.25)) * 400),   y = (math.cos(math.radians(56.25)) * 400), center = self.frameCENTER, tag = "o10"))
        self.outer_ring.append( Stone(image = self.BLANK, x = -(math.sin(math.radians(78.75)) * 400),   y = (math.cos(math.radians(78.75)) * 400),  center = self.frameCENTER, tag = "o11"))
        self.outer_ring.append( Stone(image = self.BLANK, x = -(math.sin(math.radians(78.75)) * 400),  y = -(math.cos(math.radians(78.75)) * 400),   center = self.frameCENTER, tag = "o12"))
        self.outer_ring.append( Stone(image = self.BLANK, x = -(math.sin(math.radians(56.25)) * 400),  y = -(math.cos(math.radians(56.25)) * 400),  center = self.frameCENTER, tag = "o13"))
        self.outer_ring.append( Stone(image = self.BLANK, x = -(math.sin(math.radians(33.75)) * 400),  y = -(math.cos(math.radians(33.75)) * 400),  center = self.frameCENTER, tag = "o14"))
        self.outer_ring.append( Stone(image = self.BLANK, x = -(math.sin(math.radians(11.25)) * 400),  y = -(math.cos(math.radians(11.25)) * 400),   center = self.frameCENTER, tag = "o15"))

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

        self.score = Score('Multicolore.otf', 98)
        self.score.updateScore(self.game.points)
        self.score.scorepos.right = 1400
        self.score.scorepos.centery = self.background.get_rect().centery
        self.background.blit(self.score.score, self.score.scorepos)

        self._running = True

    def on_event(self, event):

        # Check if user wants to drop the game (unlikely)
        if event.type == pygame.QUIT:
            self._running = False

        if self.gameOn:
            # Check if user pressed the right keys, turn things accordingly
            if event.type == pygame.KEYDOWN:
                if not (self.game.game_over or self.pause):
                    if (event.key == pygame.K_LEFT) or (event.key == pygame.K_RIGHT):
                        self.game.where_to_turn(self.gameKeys[pygame.key.name(event.key)])
                        self.game.new_round()

                        if self.game.current_bag == []:
                            self.game.bag()

                        self.game.insert_stone()
                    elif (event.key == pygame.K_RCTRL) or (event.key == pygame.K_LCTRL):
                        if not self.menuGameActive:
                            self.option = 0
                            self.menuGameActive = True
                        else:
                            self.menuGameActive = False

        if (self.mainMenu) or (self.menuGameActive) or (self.game.game_over):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.option = abs((self.option - 1) % len(self.menuOptions))
                elif event.key == pygame.K_DOWN:
                    self.option = abs((self.option + 1) % len(self.menuOptions))
                elif event.key == pygame.K_RETURN:
                    self.load(self.menuOptions[self.option])


    def on_loop(self):

        if self.gameOn:

            # Slow down things a bit
            clock.tick(40)

            # Refresh the state of the rings
            self.fill_rings(self.game.outer, self.outer_ring)
            self.fill_rings(self.game.middle, self.middle_ring)
            self.fill_rings(self.game.inner, self.inner_ring)

            # Refresh the score
            self.score.updateScore(self.game.points)

        return

    def on_render(self):
        # Empty screen
        self.screen.blit(self.background, (0, 0))

        if self.mainMenu:
            self.background.fill((5, 5, 5))
            self.menuMain()

        elif self.gameOn:

            self.background.fill((5, 5, 5))

            # Blit score
            self.score.scorepos.right = 1400
            self.score.scorepos.centery = self.background.get_rect().centery
            self.background.blit(self.score.score, self.score.scorepos)

            # Blit rings
            for ring in (self.outer_ring, self.middle_ring, self.inner_ring):
                for element in ring:
                    self.background.blit(element.image, element.rect)


            self.menuGame()

            # Blit game over
            if self.game.game_over:
                gOver, gOverpos = write('Game Over', 124, 'Multicolore.otf')
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
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

    def fill_rings(self, engine_ring, screen_ring):
        for indice, hole in enumerate(engine_ring):
            if engine_ring[indice] == 0:
                screen_ring[indice].updateImg(self.BLANK)
            elif engine_ring[indice] == 1:
                screen_ring[indice].updateImg(self.RED)
            elif engine_ring[indice] == 2:
                screen_ring[indice].updateImg(self.BLUE)
            elif engine_ring[indice] == 3:
                screen_ring[indice].updateImg(self.GREEN)
            elif engine_ring[indice] == 4:
                screen_ring[indice].updateImg(self.YELLOW)
            elif engine_ring[indice] == 5:
                screen_ring[indice].updateImg(self.BROWN)
            else:
                continue
        return


def main():

    game_ = Game()

    game_.on_execute()


if __name__ == '__main__': main()
