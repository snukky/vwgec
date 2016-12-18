import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from features.base_feature import BaseFeature
from logger import log


class SourcePositionFeature(BaseFeature):
    def __init__(self, weight=1.0):
        super(SourcePositionFeature, self).__init__(weight=weight)

    def extract(self, cword, csets, sentence, vector):
        vector.add_source_feature("pos={}".format(cword.pos[0]), self.weight)
