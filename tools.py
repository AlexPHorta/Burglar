# -*- encoding: utf-8 -*-
#
# Programa: descrição
#
# Copyright 2018 - Alexandre Paloschi Horta
# License: ???
#
# Website - http://www.buey.net.br


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

import os.path
import pathlib
import pickle

from utils import Colors

PUBLISHER = '.' + 'buey'
PROGRAM = 'burglar'

confPath = os.path.join(os.path.expanduser('~'), PUBLISHER, PROGRAM)
pathlib.Path(confPath).mkdir(parents=True, exist_ok=True)
confFileName = os.path.join(confPath, 'config.buey')


def saveConfigs(confs):
    with open(confFileName, 'wb') as out_s:
        for obj in confs:
            pickle.dump(obj, out_s)
    return

def loadConfigs():
    confs = []
    with open(confFileName, 'rb') as in_s:
        while True:
            try:
                obj = pickle.load(in_s)
            except EOFError:
                break
            else:
                confs.append(obj)
        return confs



try:
    # print('Loading color scheme configuration.')
    configurations = loadConfigs()
    colorScheme = configurations[0]
    # print('Loaded config file.')
except Exception as e:
    print('Cannot load saved configurations: {}'.format(e))
    configurations = None
    colorScheme = Colors()
    colorScheme.setScheme()