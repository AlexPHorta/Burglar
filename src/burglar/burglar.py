#!/usr/bin/env python


__VERSION__ = "0.1.0"

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
from enum import Enum, unique
from itertools import islice, chain, cycle

pygame.mixer.pre_init(44100, -16, 2, 4096)
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = "True"
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1, 1), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption('Burglar')

import engine
from utils import load_png, blit_alpha, write, Center, stones
from tools import saveConfigs, colorScheme, configurations


class Game:
    """The game class."""

    game_keys = {"left": 1, "right": 2}

    def __init__(self):
        """Initialize the game."""
        self._running = True
        self.level = 'normal'
        self._display_surf = None
        self.size = self.width, self.height = 1350, 1000
        self.frame_size = self.frame_width, self.frame_height = 1100, 1000
        self.inner_ring = []
        self.middle_ring = []
        self.outer_ring = []
        self.big_outer_ring = []
        self.track = pygame.mixer.music

        sound_files = {
            'splash_track': '270657__shadydave__deep-bass-growl.wav',
            'flip': '167045__drminky__slime-jump.wav',
            'click': '256116__kwahmah-02__click.wav',
            'toggle': '202312__7778__dbl-click.wav',
            'game_over_sound': '145438__soughtaftersounds__old-music-box-5.wav',
        }

        try:
            self.track.load(os.path.join(
                'sounds', '392395__shadydave__cello-marcato-loop.wav'))
            for attr, sound_file in sound_files.items():
                setattr(self, attr, pygame.mixer.Sound(
                    os.path.join('sounds', sound_file)))
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
        """Build the graphical interface of the game."""
        self.screen = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()

        self.background.fill(colorScheme.GAMEBG)
        self.gamebg = colorScheme.GAMEBGIMAGE
        self.active_screen = 0
        self.main_menu = True
        self.options_screen = False
        self.active_option = 0
        self.game_on = False
        self.game_over = False
        self.menu_game_active = False
        self.pause = False
        self.help_ = 0

        # Build the menus

        from menus import (
            ListMenu,
            SwitchableListMenu,
            FlattenedMenu,
            CreditsTextBlock,
            )

        menus_configs = {
            'mm': (
                ListMenu(
                    ('easy', 'normal', 'hard', 'options', 'help', 'credits'),
                    sizes = (58, 63),
                    bg = colorScheme.MAINMENUBG,
                    mncolors = (
                        colorScheme.MAINMENUINACTIVE,
                        colorScheme.MAINMENUACTIVE),
                    align = 'center'
                )),
            'gm': (
                SwitchableListMenu(
                    ('pause', 'quit'),
                    sizes = (52, 58, 52),
                    mncolors = (
                        colorScheme.GAMEMENUINACTIVE,
                        colorScheme.GAMEMENUACTIVE),
                    align = 'right',
                )),
            'rsm': (
                ListMenu(
                    ('resume',),
                    sizes = (52, 58),
                    mncolors = (
                        colorScheme.GAMEMENUINACTIVE,
                        colorScheme.GAMEMENUACTIVE),
                    align = 'right',
                )),
            'govm': (
                ListMenu(
                    (('new game', self.level), 'back'),
                    sizes = (52, 58),
                    mncolors = (
                        colorScheme.GAMEMENUINACTIVE,
                        colorScheme.GAMEMENUACTIVE),
                    align = 'right',
                )),
            'optm': (
                FlattenedMenu(
                    ({'Sound': ('on', 'off')}, {'Music': ('on', 'off')}, 'back'),
                    sizes = (52, 58),
                    align = 'center',
                    bg = colorScheme.OPTIONSBG,
                    mncolors = (
                        colorScheme.OPTMENUINACTIVE,
                        colorScheme.OPTMENUACTIVE),
                    hpad = 20,
                    vpad = 20,
                )),
            'hm': (
                ListMenu(
                    ('back',),
                    sizes = (58, 63),
                    mncolors = (
                        colorScheme.OPTMENUINACTIVE,
                        colorScheme.OPTMENUACTIVE),
                    align = 'center',
                )),
            'cm': (
                ListMenu(
                    ('back',),
                    sizes = (58, 63),
                    mncolors = (
                        colorScheme.OPTMENUINACTIVE,
                        colorScheme.OPTMENUACTIVE),
                    align = 'center',
                )),
        }

        for menu, conf in menus_configs.items():
            setattr(self, menu, conf)

        credits_texts = (
            ('Produced by', 'BUEY - Games and Stuff'),
            ('Programming, Testing, Artwork, Coffee', 'Alexandre Paloschi'),
            ('Website', 'www.buey.net.br'), ('Made with', 'Pygame'),
            ('Music', (
                'Marcato loop by Shady Dave',
                'https://www.freesound.org/people/ShadyDave/'))
            )

        self.credits_ = CreditsTextBlock(
            credits_texts,
            sizes = (26, 26),
            align = 'center',
            bg = colorScheme.OPTIONSBG,
            mncolors = (
                colorScheme.OPTMENUINACTIVE,
                colorScheme.OPTMENUACTIVE),
            hpad = 20,
            vpad = 10,
            )

        self.splash_screen()

    # Screen functions

    def splash_screen(self):
        """Generate the initial Buey splashscreen."""
        self.background.fill((0, 0, 0))
        bg = load_png('splash_bg.png')

        self.background.blit(bg, (0, 0))

        self.splash_track.play(1)

        for i in range(0, 255, 10):
            self.background.set_alpha(i)
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
            pygame.time.wait(10)

        buey_spritesheet = load_png('buey_sprite.png')
        buey_spritesheet_pos = buey_spritesheet.get_rect()
        buey_spritesheet_pos.centerx = self.background.get_rect().centerx
        buey_spritesheet_pos.centery = self.background.get_rect().centery

        for i in range(0, 255, 4):
            self.background.blit(bg, (0, 0))
            blit_alpha(
                self.background, buey_spritesheet, buey_spritesheet_pos, i)
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
            pygame.time.wait(10)

        pygame.time.wait(1500)

        fade_out = pygame.Surface(self.screen.get_size())

        for i in range(0, 255, 10):
            self.background.blit(bg, (0, 0))
            self.background.blit(buey_spritesheet, buey_spritesheet_pos)
            fade_out.set_alpha(i)
            self.background.blit(fade_out, (0, 0))
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
            pygame.time.wait(10)

        self.splash_track.stop()

        pygame.time.wait(200)

    def options(self):
        """Build the options screen."""
        self.game = None

        # Print Options tag
        title, title_pos = write(
            'Options', 96,
            'Multicolore.otf',
            colorScheme.OPTIONSTITLE,
            )
        title_pos.centerx = self.background.get_rect().centerx
        title_pos.centery = self.background.get_rect().height / 3
        self.background.blit(title, title_pos)

        self.optm.assemble()
        self.optm.menu_pos.centerx = self.background.get_rect().centerx
        self.optm.menu_pos.centery = 2 * (self.background.get_rect().height / 3)
        self.background.blit(self.optm.menu, self.optm.menu_pos)

    def help(self):
        """Build the help screen."""
        self.game = None
        help_file = 'help0{}.png'.format(str(self.help_))

        # Print Title
        title, title_pos = write(
            'Help', 96,
            'Multicolore.otf',
            colorScheme.OPTIONSTITLE,
            )
        title_pos.centerx = self.background.get_rect().centerx
        title_pos.centery = self.background.get_rect().height / 6
        self.background.blit(title, title_pos)

        help_image = load_png(help_file)
        help_image_pos = help_image.get_rect()
        help_image_pos.centerx = self.background.get_rect().centerx
        help_image_pos.centery = self.background.get_rect().centery
        self.background.blit(help_image, help_image_pos)

        self.hm.assemble()
        self.hm.menu_pos.centerx = self.background.get_rect().centerx
        self.hm.menu_pos.centery = 5 * (self.background.get_rect().height / 6)
        self.background.blit(self.hm.menu, self.hm.menu_pos)

    def credits(self):
        """Build the credits screen."""
        self.game = None

        # Print Options tag
        title, title_pos = write(
            'Credits', 96,
            'Multicolore.otf',
            colorScheme.OPTIONSTITLE,
            )
        title_pos.centerx = self.background.get_rect().centerx
        title_pos.centery = self.background.get_rect().height / 8
        self.background.blit(title, title_pos)

        self.credits_.assemble()
        self.credits_.menu_pos.centerx = self.background.get_rect().centerx
        self.credits_.menu_pos.centery = self.background.get_rect().centery
        self.background.blit(self.credits_.menu, self.credits_.menu_pos)

        self.cm.assemble()
        self.cm.menu_pos.centerx = self.background.get_rect().centerx
        self.cm.menu_pos.centery = 7 * (self.background.get_rect().height / 8)
        self.background.blit(self.cm.menu, self.cm.menu_pos)


    # Menus functions

    def menu_main(self):
        """Build the main menu."""
        self.game = None

        # Print game name
        title, title_pos = write(
            'Burglar', 124, 'Multicolore.otf', colorScheme.MAINMENUTITLE)
        title_pos.centerx = self.background.get_rect().centerx
        title_pos.centery = self.background.get_rect().height / 3
        self.background.blit(title, title_pos)

        self.mm.assemble()
        self.mm.menu_pos.centery = 2 * (self.background.get_rect().height / 3)
        self.mm.menu_pos.centerx = self.background.get_rect().centerx
        self.background.blit(self.mm.menu, self.mm.menu_pos)

    def menu_game(self):
        """Build the in-game menu."""
        BOTTOM_MENU_POS = 920
        RIGHT = 1300

        if not self.game_over:
            if not self.pause:
                self.gm.assemble()
                self.gm.menu_pos.bottom = BOTTOM_MENU_POS
                self.gm.menu_pos.right = 1300
                self.background.blit(self.gm.menu, self.gm.menu_pos)

                warning, warningpos = write(
                    'Press CTRL to toggle menu on/off.', 22,
                    'MankSans-Medium.ttf',
                    colorScheme.GAMEMENUWARNING)

                # Print menu warning
                warningpos.right = RIGHT
                warningpos.bottom = 950
                self.background.blit(warning, warningpos)

            else:
                self.rsm.assemble()
                self.rsm.menu_pos.bottom = BOTTOM_MENU_POS
                self.rsm.menu_pos.right = 1300
                self.background.blit(self.rsm.menu, self.rsm.menu_pos)

        else:
            self.govm.options = (('new game', self.level), 'back') # Ugly, ugly, ugly!!!!!
            self.govm.assemble()
            self.govm.menu_pos.bottom = BOTTOM_MENU_POS
            self.govm.menu_pos.right = 1300
            self.background.blit(self.govm.menu, self.govm.menu_pos)

    def load_game(self):
        """Load the game interface."""
        self.game_over = False
        self.frame = pygame.Surface(self.frame_size)
        self.frame_rect = self.frame.get_rect()
        self.frameCENTER = Center(
            self.frame_rect.centerx, self.frame_rect.centery)

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
            for coordx, multx, coordy, multy, tagg in coords[index][2]:
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
        self.score.update_score(self.game.points)

        if self.music:
            self.track.play(-1)
            self.game_over_sound_played = False

        self._running = True

    def load(self, choice, option = None):
        """Load the respective option on every menu in the game."""
        levels = ('easy', 'normal', 'hard',)
        secondaries = {
            'options': 1, 'help': 3, 'credits': 4, 'quit': 0, 'back': 0,}
        choice = str(choice)
        option = str(option)
        if choice in levels:
            self.active_screen = 2
            self.level = choice
            self.load_game()
        elif choice in secondaries:
            self.active_screen = secondaries[choice]
            self.gm.switch('off')
            if choice not in ('quit', 'back'):
                getattr(self, choice)()
            else:
                self.menu_main()
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

    def on_event(self, event):
        """Run the event checking routine."""

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
            selected_option = getattr(screen, keys[event_.key][0])
            selected_option_sound = getattr(self, keys[event_.key][1])
            if self.sound: selected_option_sound.play()
            if event_.key != pygame.K_RETURN:
                selected_option()
            else:
                if screen == self.mm:
                    self.load(selected_option())
                elif screen == self.optm:
                    self.load(*selected_option())

        def options_screen(event_):
            main_menu(event_, screen = self.optm)

        def game_on(event_):
            # Check if user pressed the right keys, turn things accordingly
            if not (self.game_over or self.pause):
                if (event_.key == pygame.K_LEFT) or (event_.key == pygame.K_RIGHT):
                    self.game.where_to_turn(self.game_keys[pygame.key.name(event_.key)])
                    self.game.new_round()

                    self.game.insert_stone()

                elif event_.key in (pygame.K_RCTRL, pygame.K_LCTRL):
                    if self.gm.switchedOn:
                        if self.sound: self.toggle.play()
                        self.gm.switch('off')
                    else:
                        if self.sound: self.toggle.play()
                        self.gm.switch('on')

            if self.game_over:
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
            keys = {
                pygame.K_LEFT: (-1, self.flip, lambda: 'help'),
                pygame.K_RIGHT: (1, self.flip, lambda: 'help'),
                pygame.K_RETURN: (0, self.click, self.hm.select),
            }
            if event_.key in keys:
                self.help_ = abs((self.help_ + keys[event_.key][0]) % 6) #TODO Remove this 6
                if self.sound: keys[event_.key][1].play()
                self.load(keys[event_.key][2]())

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
            screens[self.active_screen](event)

        return

    def on_loop(self):
        """Run the loop routine."""

        # Slow down things a bit
        clock.tick(20)

        if self.active_screen == 2: #self.game_on:

            # Refresh the state of the rings
            self.fill_rings(self.game.big_outer, self.big_outer_ring)
            self.fill_rings(self.game.outer, self.outer_ring)
            self.fill_rings(self.game.middle, self.middle_ring)
            self.fill_rings(self.game.inner, self.inner_ring)

            # Refresh the score
            self.score.update_score(self.game.points)

            self.game_over = self.game.game_over

            if self.game_over:
                self.track.stop()

                if not self.game_over_sound_played:
                    self.game_over_sound.play()
                    self.game_over_sound_played = True

        return

    def on_render(self):
        """Run the screen renderization routine."""
        # Empty the screen
        self.screen.blit(self.background, (0, 0))

        def main_menu():
        # if self.active_screen == 0: #self.main_menu:
            self.background.fill(colorScheme.MAINMENUBG)
            self.menu_main()

        def options_screen():
        # elif self.active_screen == 1: #self.options_screen:
            self.background.fill(colorScheme.OPTIONSBG)
            self.options()

        def game_on():
        # elif self.active_screen == 2: #self.game_on:

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

            self.menu_game()

            # Blit game over
            if self.game_over:
                game_over_semi_trans = load_png('game_over.png')
                game_over_semi_trans_pos = game_over_semi_trans.get_rect()
                game_over_semi_trans_pos.center = self.frameCENTER

                game_over, game_over_pos = write(
                    'Game Over', 124,
                    'Multicolore.otf',
                    colorScheme.GAMEOVER,
                    )
                game_over_pos.centerx, game_over_pos.centery = (
                    self.frame.get_rect().center)

                self.background.blit(
                    game_over_semi_trans, game_over_semi_trans_pos)

                self.background.blit(game_over, game_over_pos)

        def help_screen():
        # elif self.active_screen == 3:

            self.background.fill(colorScheme.OPTIONSBG)
            self.help()

        def credits_screen():
        # elif self.active_screen == 4:

            self.background.fill(colorScheme.OPTIONSBG)
            self.credits()

        screens = {
            0: main_menu,
            1: options_screen,
            2: game_on,
            3: help_screen,
            4: credits_screen,
        }

        screens[self.active_screen]()

        self.screen.blit(self.background, (0, 0))

        # Refresh everything
        pygame.display.flip()
        return

    def on_cleanup(self):
        """Prepare the game for exiting."""
        confs = (colorScheme, self.music, self.sound)
        saveConfigs(confs)
        pygame.quit()
        return

    def on_execute(self):
        """Run the main game loop."""
        if self.on_init() == False:
            self._running = False
        while self._running:
            self.on_event(pygame.event.wait())
            self.on_loop()
            self.on_render()
        self.on_cleanup()

    def fill_rings(self, engine_ring, screen_ring):
        """Fill the grid with stones."""
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


class Stone(pygame.sprite.Sprite):
    """A stone that sits still and just changes colors.
    Returns: stone object
    Functions: update
    Attributes: area
    """

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
    """The game score class."""

    def __init__(self,
        font = None,
        size = 10,
        color = (0, 0, 0),
        bgcolor = None):
        """Build the game score.

        Keyword arguments:
        font -- A font name (string).
        size -- The size of the font (int).
        color -- The color of the font, in format r, g, b (tuple).
        bgcolor -- The background color of the score, in format r, g, b (tuple).
        """
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

    def update_score(self, newScore):
        """Update the score."""
        self.points = newScore
        self.score = self.font.render(
            str(self.points), True, self.color, self.bgcolor)
        self.score = self.score.convert_alpha()
        self.scorepos = self.score.get_rect()
        return


def main():

    game_ = Game()

    game_.on_execute()


if __name__ == '__main__': main()
