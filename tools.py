#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Burglar: a game of stones
#
#    Copyright 2018 - Alexandre Paloschi Horta
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# Website - http://www.buey.net.br/burglar


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
    print(f'Cannot load saved configurations: {e}')
    configurations = None
    colorScheme = Colors()
    colorScheme.setScheme()
