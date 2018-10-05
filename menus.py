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


from tools import colorScheme
from utils import write, toRGBA


class ListMenu:

    def __init__(self, opt, align = 'left', font = 'Multicolore.otf', sizes = (10, 10), \
        bg = '#AAAAAA', mncolors = ('#FFFFFF', '#AAAAAA'), hpad = 0, vpad = 0):
        self.options = opt
        self.selected = 0
        self.align = str(align)
        self.font = str(font)
        self.hpad = hpad
        self.vpad = vpad
        self.mncolors = mncolors
        self.bg = (0, 0, 0, 0)

        try:
            self.defaultOpt, self.selectedOpt = sizes
        except ValueError:
            self.defaultOpt, self.selectedOpt, off = sizes
            self.off = off


    def up(self):
        self.selected = abs((self.selected - 1) % len(self.options))

    def down(self):
        self.selected = abs((self.selected + 1) % len(self.options))

    def select(self):
        return self.signals[self.selected]

    def prepare(self):
        self.fontDefault = {'size': self.defaultOpt, 'color': self.mncolors[0]}
        self.fontSelected = {'size': self.selectedOpt, 'color': self.mncolors[1]}
        self.toPrint = []
        self.signals = []
        for index, item in enumerate(self.options):
            if not isinstance(item, tuple):
                self.signals.append(item)
                if index == self.selected:
                    menuItem, menuItemPos = write(item, self.fontSelected['size'], self.font, self.fontSelected['color'])
                else:
                    menuItem, menuItemPos = write(item, self.fontDefault['size'], self.font, self.fontDefault['color'])
            else:
                self.signals.append(item[1])
                if index == self.selected:
                    menuItem, menuItemPos = write(item[0], self.fontSelected['size'], self.font, self.fontSelected['color'])
                else:
                    menuItem, menuItemPos = write(item[0], self.fontDefault['size'], self.font, self.fontDefault['color'])
            self.toPrint.append((menuItem, menuItemPos))
        self.menuWidth = int(max([x[0].get_width() for x in self.toPrint]))
        self.menuHeight = int(sum([x[0].get_height() for x in self.toPrint]) + (len(self.toPrint) * self.vpad))
        return

    def assemble(self):
        self.prepare()
        dispBy = 0
        self.menuFrame = pygame.Surface((self.menuWidth, self.menuHeight)).convert_alpha()
        self.menuFrame.fill(self.bg)
        for item in self.toPrint:
            if self.align == 'center':
                item[1].centerx = self.menuFrame.get_rect().centerx
            elif self.align == 'right':
                item[1].right = self.menuFrame.get_rect().right
            self.menuFrame.blit(item[0], (item[1].x, (item[1].y + dispBy)))
            dispBy += item[0].get_height() + self.vpad
        self.menu, self.menuPos = self.menuFrame, self.menuFrame.get_rect()


class SwitchableListMenu(ListMenu):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fontSwitchedOff = {'size': self.off, 'color': colorScheme.GAMEMENUSWITCHEDOFF}
        self.switchedOn = False

    def switch(self, state):
        if state == 'on':
            self.switchedOn = True
        if state == 'off':
            self.switchedOn = False

    def prepare(self):
        self.fontDefault = {'size': self.defaultOpt, 'color': self.mncolors[0]}
        self.fontSelected = {'size': self.selectedOpt, 'color': self.mncolors[1]}
        self.toPrint = []
        self.signals = []
        if not self.switchedOn:
            self.selected = 0
        for index, item in enumerate(self.options):
            if not isinstance(item, tuple):
                self.signals.append(item)
                if index == self.selected:
                    if self.switchedOn:
                        menuItem, menuItemPos = write(item, self.fontSelected['size'], self.font, self.fontSelected['color'])
                    else:
                        menuItem, menuItemPos = write(item, self.fontSwitchedOff['size'], self.font, self.fontSwitchedOff['color'])
                else:
                    if self.switchedOn:
                        menuItem, menuItemPos = write(item, self.fontDefault['size'], self.font, self.fontDefault['color'])
                    else:
                        menuItem, menuItemPos = write(item, self.fontSwitchedOff['size'], self.font, self.fontSwitchedOff['color'])
            else:
                self.signals.append(item[1])
                if index == self.selected:
                    if self.switchedOn:
                        menuItem, menuItemPos = write(item[1], self.fontSelected['size'], self.font, self.fontSelected['color'])
                    else:
                        menuItem, menuItemPos = write(item[1], self.fontSwitchedOff['size'], self.font, self.fontSwitchedOff['color'])
                else:
                    if self.switchedOn:
                        menuItem, menuItemPos = write(item[1], self.fontDefault['size'], self.font, self.fontDefault['color'])
                    else:
                        menuItem, menuItemPos = write(item[1], self.fontSwitchedOff['size'], self.font, self.fontSwitchedOff['color'])
            self.toPrint.append((menuItem, menuItemPos))
        self.menuWidth = int(max([x[0].get_width() for x in self.toPrint]))
        self.menuHeight = int(sum([x[0].get_height() for x in self.toPrint]))
        return


class FlattenedMenu(ListMenu):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active = 0


    def prepare(self):
        self.fontDefault = {'size': self.defaultOpt, 'color': self.mncolors[0]}
        self.fontSelected = {'size': self.selectedOpt, 'color': self.mncolors[1]}
        self.toPrint = []
        self.signals = []
        for index, item in enumerate(self.options):
            if not isinstance(item, dict):
                self.signals.append(item)
                if index == self.selected:
                    menuItem, menuItemPos = write(item, self.fontSelected['size'], self.font, self.fontSelected['color'])
                else:
                    menuItem, menuItemPos = write(item, self.fontDefault['size'], self.font, colorScheme.GAMEMENUSWITCHEDOFF)
            else:
                for tag, opts in item.items():
                    tag_ = tag.lower()
                    self.signals.append((opts, tag_))
                    if index == self.selected:
                        tag, tagPos = write(tag, self.fontSelected['size'], self.font, colorScheme.OPTMENUTAG)
                        if 0 == self.active:
                            menuItem1, menuItem1Pos = write(opts[0], self.fontSelected['size'], self.font, colorScheme.OPTMENUACTIVE)
                            menuItem2, menuItem2Pos = write(opts[1], self.fontDefault['size'], self.font, colorScheme.OPTMENUINACTIVE)
                        else:
                            menuItem1, menuItem1Pos = write(opts[0], self.fontDefault['size'], self.font, colorScheme.OPTMENUINACTIVE)
                            menuItem2, menuItem2Pos = write(opts[1], self.fontSelected['size'], self.font, colorScheme.OPTMENUACTIVE)
                    else:
                        tag, tagPos = write(tag, self.fontDefault['size'], self.font, colorScheme.GAMEMENUSWITCHEDOFF)
                        menuItem1, menuItem1Pos = write(opts[0], self.fontDefault['size'], self.font, colorScheme.GAMEMENUSWITCHEDOFF)
                        menuItem2, menuItem2Pos = write(opts[1], self.fontDefault['size'], self.font, colorScheme.GAMEMENUSWITCHEDOFF)
                    menuItem1Pos.left = tagPos.right + (2 * self.hpad)
                    menuItem2Pos.left = menuItem1Pos.right + self.hpad
                    menuItemWidth = int(sum([x.get_width() for x in (tag, menuItem1, menuItem2)]) + (3 * self.hpad))
                    menuItemHeight = int(max([x.get_height() for x in (tag, menuItem1, menuItem2)]))
                    menuItem = pygame.Surface((menuItemWidth, menuItemHeight)).convert_alpha()
                    menuItem.fill((0, 0, 0, 0))
                    menuItem.blit(tag, (0, 0))
                    menuItem.blit(menuItem1, menuItem1Pos)
                    menuItem.blit(menuItem2, menuItem2Pos)
                    menuItemPos = menuItem.get_rect()
            self.toPrint.append((menuItem, menuItemPos))
        self.menuWidth = int(max([x[0].get_width() for x in self.toPrint]))
        self.menuHeight = int(sum([x[0].get_height() for x in self.toPrint]) + (len(self.toPrint) * self.vpad))
        return

    def left(self):
        self.active = abs((self.active - 1) % len(self.signals[self.selected]))

    def right(self):
        self.active = abs((self.active + 1) % len(self.signals[self.selected]))

    def select(self):
        if isinstance(self.signals[self.selected], tuple):
            return self.signals[self.selected][0][self.active], self.signals[self.selected][1]
        else:
            return (self.signals[self.selected],)
