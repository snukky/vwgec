import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from logger import log


class BaseFeature(object):
    def __init__(self, window=3, factor=0):
        self.window = window
        self.factor = factor

    def extract(self, cword, csets, sentence, vector):
        raise NotImplementedError()

    def left_context(self, pos, sentence, window=None, factor=None):
        window = self.window if window is None else window
        factor = self.factor if factor is None else factor

        start = max(0, pos[0] - window)
        bos_size = max(0, window - pos[0])
        return (["<s>"] * bos_size) + sentence[factor][start:pos[0]]

    def right_context(self, pos, sentence, window=None, factor=None):
        window = self.window if window is None else window
        factor = self.factor if factor is None else factor

        num_toks = len(sentence[factor])
        end = min(num_toks, pos[1] + window)
        eos_size = max(0, pos[1] + window - num_toks)
        return sentence[factor][pos[1]:end] + (["</s>"] * eos_size)

    def both_contexts(self, pos, sentence, window=None, factor=None):
        return (self.left_context(pos, sentence, window, factor),
                self.right_context(pos, sentence, window, factor))

    def __str__(self):
        return self.__class__
