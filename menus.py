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


# pygame.init()
# clock = pygame.time.Clock()
# screen = pygame.display.set_mode((1, 1), pygame.HWSURFACE | pygame.DOUBLEBUF)
# pygame.display.set_caption('Burglar')

# screen = pygame.display.set_mode((1350, 1000), pygame.HWSURFACE | pygame.DOUBLEBUF)
# background = pygame.Surface(screen.get_size())
# background = background.convert()
# background.fill((0, 0, 0))

from utils import colorScheme
from utils import write


class ListMenu:

    def __init__(self, opt, align = 'left', font = 'Multicolore.otf', sizes = (10, 10), bg = colorScheme.BACKGROUND):
        self.options = opt
        self.selected = 0
        self.align = str(align)
        self.font = str(font)

        try:
            default, selected = sizes
        except ValueError:
            default, selected, off = sizes
            self.off = off

        self.fontDefault = {'size': default, 'color': colorScheme.MENUINACTIVE}
        self.fontSelected = {'size': selected, 'color': colorScheme.MENUACTIVE}
        self.bg = bg

    def up(self):
        self.selected = abs((self.selected - 1) % len(self.options))

    def down(self):
        self.selected = abs((self.selected + 1) % len(self.options))

    def select(self):
        return self.signals[self.selected]

    def prepare(self):
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
        self.menuHeight = int(sum([x[0].get_height() for x in self.toPrint]))
        return

    def assemble(self):
        self.prepare()
        dispBy = 0
        self.menuFrame = pygame.Surface((self.menuWidth, self.menuHeight)).convert()
        self.menuFrame.fill(self.bg)
        for item in self.toPrint:
            if self.align == 'center':
                item[1].centerx = self.menuFrame.get_rect().centerx
            elif self.align == 'right':
                item[1].right = self.menuFrame.get_rect().right
            self.menuFrame.blit(item[0], (item[1].x, (item[1].y + dispBy)))
            dispBy += item[0].get_height()
        self.menu, self.menuPos = self.menuFrame, self.menuFrame.get_rect()


class SwitchableListMenu(ListMenu):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fontSwitchedOff = {'size': self.off, 'color': colorScheme.MENUSWITCHEDOFF}
        self.switchedOn = False

    def switch(self, state):
        if state == 'on':
            self.switchedOn = True
        if state == 'off':
            self.switchedOn = False

    def prepare(self):
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
        self.toPrint = []
        self.signals = []
        for index, item in enumerate(self.options):
            if not isinstance(item, dict):
                self.signals.append(item)
                if index == self.selected:
                    menuItem, menuItemPos = write(item, self.fontSelected['size'], self.font, self.fontSelected['color'])
                else:
                    menuItem, menuItemPos = write(item, self.fontDefault['size'], self.font, colorScheme.MENUSWITCHEDOFF)
            else:
                for tag, opts in item.items():
                    self.signals.append(opts)
                    if index == self.selected:
                        tag, tagPos = write(tag, self.fontSelected['size'], self.font, colorScheme.OPTMENUTAG)
                        if 0 == self.active:
                            menuItem1, menuItem1Pos = write(opts[0], self.fontSelected['size'], self.font, colorScheme.MENUACTIVE)
                            menuItem2, menuItem2Pos = write(opts[1], self.fontDefault['size'], self.font, colorScheme.MENUINACTIVE)
                        else:
                            menuItem1, menuItem1Pos = write(opts[0], self.fontDefault['size'], self.font, colorScheme.MENUINACTIVE)
                            menuItem2, menuItem2Pos = write(opts[1], self.fontSelected['size'], self.font, colorScheme.MENUACTIVE)
                    else:
                        tag, tagPos = write(tag, self.fontDefault['size'], self.font, colorScheme.MENUSWITCHEDOFF)
                        menuItem1, menuItem1Pos = write(opts[0], self.fontDefault['size'], self.font, colorScheme.MENUSWITCHEDOFF)
                        menuItem2, menuItem2Pos = write(opts[1], self.fontDefault['size'], self.font, colorScheme.MENUSWITCHEDOFF)
                    menuItem1Pos.left = tagPos.right
                    menuItem2Pos.left = menuItem1Pos.right
                    menuItemWidth = int(sum([x.get_width() for x in (tag, menuItem1, menuItem2)]))
                    menuItemHeight = int(max([x.get_height() for x in (tag, menuItem1, menuItem2)]))
                    menuItem = pygame.Surface((menuItemWidth, menuItemHeight)).convert()
                    menuItem.fill(self.bg)
                    menuItem.blit(tag, (0, 0))
                    menuItem.blit(menuItem1, menuItem1Pos)
                    menuItem.blit(menuItem2, menuItem2Pos)
                    menuItemPos = menuItem.get_rect()
            self.toPrint.append((menuItem, menuItemPos))
        self.menuWidth = int(max([x[0].get_width() for x in self.toPrint]))
        self.menuHeight = int(sum([x[0].get_height() for x in self.toPrint]))
        print('{} - {}'.format(self.selected, self.active))
        return

    def left(self):
        self.active = abs((self.active - 1) % len(self.signals[self.selected]))

    def right(self):
        self.active = abs((self.active + 1) % len(self.signals[self.selected]))


# menu = ListMenu(('easy', 'normal', 'hard', 'options', 'help'), align = 'center')

# count = 0
# while count < 91600:
#     print(count)
#     background.blit(menu.menu, (0, 0))
#     screen.blit(background, (0, 0))
#     pygame.display.flip()
#     count += 1