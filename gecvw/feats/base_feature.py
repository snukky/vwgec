import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from logger import log


class BaseFeature(object):
    def __init__(self):
        pass

    def extract(self, cword, csets, sentence, vector):
        raise NotImplementedError()

    def left_context(self, pos, sentence, factors=[]):
        pass

    def right_context(self, pos, sentence, factors=[]):
        pass

    def __str__(self):
        return self.__class__
