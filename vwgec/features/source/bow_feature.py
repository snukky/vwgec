import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from features.base_feature import BaseFeature
from logger import log


class BOWFeature(BaseFeature):
    def __init__(self, window=3, factor=0, weight=1.0):
        super(BOWFeature, self).__init__(
            window=window, factor=factor, weight=weight)

    def extract(self, cword, csets, sentence, vector):
        left_cntx, right_cntx = self.both_contexts(cword.pos, sentence)
        for word in set(left_cntx + right_cntx):
            vector.add_source_feature("bow={}".format(word), self.weight)
