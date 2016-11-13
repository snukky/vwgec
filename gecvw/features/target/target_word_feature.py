import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from features.base_feature import BaseFeature
from logger import log


class TargetWordFeature(BaseFeature):
    def extract(self, cword, csets, sentence, vector):
        for tgt_cw in csets.tgt:
            tgt = csets.construct_target_word(cword.err, cword.src, tgt_cw)
            vector.add_target_feature(tgt_cw, "tgt={}".format(tgt.lower()))
