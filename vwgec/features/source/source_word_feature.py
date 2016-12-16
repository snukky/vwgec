import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from features.base_feature import BaseFeature
from logger import log


class SourceWordFeature(BaseFeature):
    def __init__(self, factor=0, weight=1.0):
        super(SourceWordFeature, self).__init__(factor=factor, weight=weight)

    def extract(self, cword, csets, sentence, vector):
        err = ' '.join(sentence[self.factor][cword.pos[0]:cword.pos[1]])
        vector.add_source_feature("err={}".format(err.lower()), self.weight)
