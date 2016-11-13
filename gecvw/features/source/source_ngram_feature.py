import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from features.base_feature import BaseFeature
from logger import log


class SourceNGramFeature(BaseFeature):
    def __init__(self, window=3, factor=0):
        self.window = window
        self.factor = factor

    def extract(self, cword, csets, sentence, vector):
        for num_words_after in xrange(self.window + 1):
            num_words_before = self.window - num_words_after

            ngram = []
            for i in xrange(cword.pos[0] - num_words_before, cword.pos[0]):
                ngram.append("<s>" if i < 0 else sentence[i])
            for i in xrange(cword.pos[1], cword.pos[1] + num_words_after):
                ngram.append("</s>" if i >= len(sentence) else sentence[i])

            feat = "ngram^{}={}".format(num_words_before, ' '.join(ngram))
            vector.add_source_feature(feat.lower())