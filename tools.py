# -*- encoding: utf-8 -*-
#
# Programa: descrição
#
# Copyright 2018 - Alexandre Paloschi Horta
# License: ???
#
# Website - http://www.buey.net.br


import os.path
import pathlib
import pickle


PUBLISHER = '.' + 'buey'
PROGRAM = 'burglar'

confPath = os.path.join(os.path.expanduser('~'), PUBLISHER, PROGRAM)
pathlib.Path(confPath).mkdir(parents=True, exist_ok=True)
confFileName = os.path.join(confPath, 'config.buey')


def saveConfigs(object):
    with open(confFileName, 'wb') as out_s:
        pickle.dump(object, out_s)
    return

def loadConfigs():
    with open(confFileName, 'rb') as in_s:
        return pickle.load(in_s)
