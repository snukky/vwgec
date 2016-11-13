import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from features.base_feature import BaseFeature
from logger import log


class BOWFeature(BaseFeature):
    def __init__(self, window=3, factor=0):
        self.window = window
        self.factor = factor

    def extract(self, cword, csets, sentence, vector):
        left_cntx, right_cntx = self.both_contexts(cword.pos, sentence)
        for word in set(left_cntx + right_cntx):
            vector.add_source_feature("bow={}".format(word))
