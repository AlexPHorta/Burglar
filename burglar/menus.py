#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#

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
    print(f"Couldn't load module: {err}.")
    sys.exit(2)


from tools import colorScheme
from utils import write, toRGBA


class ListMenu:

    def __init__(self,
        opt,
        align = 'left',
        font = 'Multicolore.otf',
        sizes = (10, 10),
        bg = '#AAAAAA',
        mncolors = ('#FFFFFF', '#AAAAAA'),
        hpad = 0,
        vpad = 0
        ):
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
        self.fontDefault = {
            'size': self.defaultOpt, 'color': toRGBA(self.mncolors[0])}
        self.fontSelected = {
            'size': self.selectedOpt, 'color': toRGBA(self.mncolors[1])}
        self.toPrint = []
        self.signals = []

        for index, item in enumerate(self.options):
            fontMenuItem = self.fontSelected if index == self.selected\
                else self.fontDefault
            toWrite = item if not isinstance(item, tuple) else item[0]
            self.signals.append(item) if not isinstance(item, tuple)\
                else self.signals.append(item[1])
            menuItem, menuItemPos = write(
                toWrite, fontMenuItem['size'], self.font, fontMenuItem['color'])
            self.toPrint.append((menuItem, menuItemPos))
        self.menuWidth = int(max([x[0].get_width() for x in self.toPrint]))
        self.menuHeight = int(
            sum([x[0].get_height() for x in self.toPrint])
            + (len(self.toPrint) * self.vpad))
        return

    def assemble(self):
        self.prepare()
        dispBy = 0
        self.menuFrame = pygame.Surface(
            (self.menuWidth, self.menuHeight)).convert_alpha()
        self.menuFrame.fill(self.bg)
        for item in self.toPrint:
            if self.align == 'center':
                item[1].centerx = self.menuFrame.get_rect().centerx
            elif self.align == 'right':
                item[1].right = self.menuFrame.get_rect().right
            self.menuFrame.blit(item[0], (item[1].x, (item[1].y + dispBy)))
            dispBy += item[0].get_height() + self.vpad
        self.menu, self.menu_pos = self.menuFrame, self.menuFrame.get_rect()


class SwitchableListMenu(ListMenu):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fontSwitchedOff = {
            'size': self.off, 'color': colorScheme.GAMEMENUSWITCHEDOFF}
        self.switchedOn = False

    def switch(self, state):
        switch = {'on': True, 'off': False}
        self.switchedOn = switch[state]

    def prepare(self):
        self.fontDefault = {'size': self.defaultOpt, 'color': self.mncolors[0]}
        self.fontSelected = {'size': self.selectedOpt, 'color': self.mncolors[1]}
        self.toPrint = []
        self.signals = []
        if not self.switchedOn:
            self.selected = 0
        for index, item in enumerate(self.options):
            itemOption = item if not isinstance(item, tuple) else item[1]
            self.signals.append(itemOption)
            if self.switchedOn:
                fontSelectedMenuItem = (
                    self.fontSelected if index == self.selected
                    else self.fontDefault)
                menuItem, menuItemPos = write(
                    itemOption, fontSelectedMenuItem['size'],
                    self.font, fontSelectedMenuItem['color'])
            else:
                menuItem, menuItemPos = write(
                    itemOption, self.fontSwitchedOff['size'],
                    self.font, self.fontSwitchedOff['color'])
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
                    menuItem, menuItemPos = write(
                        item, self.fontSelected['size'],
                        self.font, self.fontSelected['color'])
                else:
                    menuItem, menuItemPos = write(
                        item, self.fontDefault['size'],
                        self.font, colorScheme.GAMEMENUSWITCHEDOFF)
            else:
                for tag, opts in item.items():
                    tag_ = tag.lower()
                    self.signals.append((opts, tag_))
                    if index == self.selected:
                        tag, tagPos = write(
                            tag, self.fontSelected['size'],
                            self.font, colorScheme.OPTMENUTAG)
                        if 0 == self.active:
                            menuItem1, menuItem1Pos = write(
                                opts[0], self.fontSelected['size'],
                                self.font, colorScheme.OPTMENUACTIVE)
                            menuItem2, menuItem2Pos = write(
                                opts[1], self.fontDefault['size'],
                                self.font, colorScheme.OPTMENUINACTIVE)
                        else:
                            menuItem1, menuItem1Pos = write(
                                opts[0], self.fontDefault['size'],
                                self.font, colorScheme.OPTMENUINACTIVE)
                            menuItem2, menuItem2Pos = write(
                                opts[1], self.fontSelected['size'],
                                self.font, colorScheme.OPTMENUACTIVE)
                    else:
                        tag, tagPos = write(
                            tag, self.fontDefault['size'], self.font,
                            colorScheme.GAMEMENUSWITCHEDOFF)
                        menuItem1, menuItem1Pos = write(
                            opts[0], self.fontDefault['size'],
                            self.font, colorScheme.GAMEMENUSWITCHEDOFF)
                        menuItem2, menuItem2Pos = write(
                            opts[1], self.fontDefault['size'], self.font,
                            colorScheme.GAMEMENUSWITCHEDOFF)
                    menuItem1Pos.left = tagPos.right + (2 * self.hpad)
                    menuItem2Pos.left = menuItem1Pos.right + self.hpad
                    menuItemWidth = int(
                        sum([x.get_width() for x
                            in (tag, menuItem1, menuItem2)]) + (3 * self.hpad))
                    menuItemHeight = int(
                        max([x.get_height() for x
                            in (tag, menuItem1, menuItem2)]))
                    menuItem = pygame.Surface(
                        (menuItemWidth, menuItemHeight)).convert_alpha()
                    menuItem.fill((0, 0, 0, 0))
                    menuItem.blit(tag, (0, 0))
                    menuItem.blit(menuItem1, menuItem1Pos)
                    menuItem.blit(menuItem2, menuItem2Pos)
                    menuItemPos = menuItem.get_rect()
            self.toPrint.append((menuItem, menuItemPos))
        self.menuWidth = int(max([x[0].get_width() for x in self.toPrint]))
        self.menuHeight = int(
            sum([x[0].get_height() for x
            in self.toPrint]) + (len(self.toPrint) * self.vpad))
        return

    def left(self):
        self.active = abs((self.active - 1) % len(self.signals[self.selected]))

    def right(self):
        self.active = abs((self.active + 1) % len(self.signals[self.selected]))

    def select(self):
        if isinstance(self.signals[self.selected], tuple):
            return (self.signals[self.selected][0][self.active],
                self.signals[self.selected][1])
        else:
            return (self.signals[self.selected],)


class CreditsTextBlock(FlattenedMenu):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def prepare(self):
        self.fontDefault = {'size': self.defaultOpt, 'color': self.mncolors[0]}
        self.toPrint = []
        for key, value in self.options:
            self.menuItems = []
            tag, tagPos = write(
                key, self.fontDefault['size'],
                self.font, colorScheme.OPTMENUTAG)
            if not isinstance(value, tuple):
                menuItem1, menuItem1Pos = write(
                    value, self.fontDefault['size'],
                    self.font, colorScheme.OPTMENUACTIVE)
                menuItem1Pos.top = tagPos.bottom + self.vpad
                menuItemWidth = int(
                    max([x.get_width() for x in (tag, menuItem1)]))
                menuItemHeight = int(
                    sum([x.get_height() for x
                    in (tag, menuItem1)]) + (3 * self.vpad))
            else:
                for item in value:
                    menuItem1, menuItem1Pos = write(
                        item, self.fontDefault['size'], self.font,
                        colorScheme.OPTMENUACTIVE)
                    menuItem1Pos.top = tagPos.bottom + self.vpad
                    self.menuItems.append((menuItem1, menuItem1Pos))
                    menuItemWidth = int(
                        max([x.get_width() for x in (tag, menuItem1)]))
                    menuItemHeight = int(
                        sum([x.get_height() for x
                        in (tag, menuItem1)]) + (3 * self.vpad))

            menuItem = pygame.Surface(
                (menuItemWidth, menuItemHeight)).convert_alpha()
            menuItemPos = menuItem.get_rect()
            menuItem.fill((0, 0, 0, 0))

            tagPos.centerx = menuItemPos.centerx
            menuItem1Pos.centerx = menuItemPos.centerx

            menuItem.blit(tag, tagPos)
            if not isinstance(value, tuple):
                menuItem.blit(menuItem1, menuItem1Pos)
            else:
                for index, item in enumerate(self.menuItems):
                    itemPos = item[0].get_rect()
                    itemPos.centerx = menuItemPos.centerx
                    itemPos.top = tagPos.bottom + self.vpad + (
                        item[0].get_height() * (index))
                    menuItem.blit(item[0], itemPos)
            self.toPrint.append((menuItem, menuItemPos))
        self.menuWidth = int(max([x[0].get_width() for x in self.toPrint]))
        self.menuHeight = int(
            sum([x[0].get_height() for x
            in self.toPrint]) + (len(self.toPrint) * self.vpad))
        return

    def left(self):
        pass

    def right(self):
        pass

    def select(self):
        return (self.signals[self.selected],)
