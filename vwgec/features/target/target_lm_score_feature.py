import os
import sys
import kenlm
import math

sys.path.insert(0, os.path.dirname(__file__))

from features.base_feature import BaseFeature
from logger import log



class TargetLMScoreFeature(BaseFeature):
    def __init__(self, lm=None, size=2, factor=0, weight=1.0):
        super(TargetLMScoreFeature, self).__init__(
            window=size, factor=factor, weight=weight)

        log.info("Load language model: {}".format(lm))
        self.kenlm = kenlm.Model(lm)
        log.info("Load {}-gram model".format(self.kenlm.order))

    def extract(self, cword, csets, sentence, vector):
        for tgt_cw in csets.tgt:
            tgt = csets.construct_target_word(cword.err, cword.src, tgt_cw)
            left_cntx, right_cntx = self.both_contexts(cword.pos, sentence)
            if tgt:
                toks = left_cntx + [tgt] + right_cntx
            else:
                toks = left_cntx + right_cntx
            sent = ' '.join(toks)
            # TODO: moze dzielic przez stala wartosc?
            score = self.kenlm.score(sent)

            feat = "lm{}^{}={}".format(self.factor, self.window, tgt.lower())
            weight = self.weight * self.normalize_score(score)
            vector.add_target_feature(tgt_cw, feat, weight)

    def normalize_score(self, score):
        return math.exp(score / (self.window * 2.0)) * 10
