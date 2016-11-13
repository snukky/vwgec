import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from logger import log


class BaseFeature(object):
    def __init__(self):
        self.window = 3
        self.factor = 0

    def extract(self, cword, csets, sentence, vector):
        raise NotImplementedError()

    def left_context(self, pos, sentence, window=None, factor=None):
        window = self.window if window is None else window
        factor = self.factor if factor is None else factor

        start = max(0, pos[0] - window)
        bos_size = max(0, window - pos[0])
        return (["<s>"] * bos_size) + sentence[start:pos[0]]

    def right_context(self, pos, sentence, window=None, factor=None):
        window = self.window if window is None else window
        factor = self.factor if factor is None else factor

        end = min(len(sentence), pos[1] + window)
        eos_size = max(0, pos[1] + window - len(sentence))
        return sentence[pos[1]:end] + (["</s>"] * eos_size)

    def both_contexts(self, pos, sentence, window=None, factor=None):
        return (self.left_context(pos, sentence, window, factor),
                self.right_context(pos, sentence, window, factor))

    def __str__(self):
        return self.__class__
