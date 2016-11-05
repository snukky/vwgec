import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from feats.base_feature import BaseFeature
from logger import log


class TargetWordFeature(BaseFeature):
    def extract(self, cword, csets, sentence, vector):
        for cw in csets.tgt:
            vector.add_target_feature(cw, "tgt={}".format('xxx'))
