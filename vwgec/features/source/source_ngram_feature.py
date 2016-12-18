import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from features.base_feature import BaseFeature
from logger import log


class SourceNGramFeature(BaseFeature):
    def __init__(self, size=3, factor=0, weight=1.0, exceed=False):
        super(SourceNGramFeature, self).__init__(
            window=size, factor=factor, weight=weight)
        self.exceed = exceed

    def extract(self, cword, csets, sentence, vector):
        sentence = sentence[self.factor]
        for num_words_after in xrange(self.window + 1):
            num_words_before = self.window - num_words_after

            # Do not allow for more than single <s> or </s>.
            if not self.exceed and (
                    self.bos_size(cword.pos) > 1 or
                    self.eos_size(cword.pos, len(sentence)) > 1):
                continue

            ngram = []
            for i in xrange(cword.pos[0] - num_words_before, cword.pos[0]):
                ngram.append("<s>" if i < 0 else sentence[i])
            for i in xrange(cword.pos[1], cword.pos[1] + num_words_after):
                ngram.append("</s>" if i >= len(sentence) else sentence[i])

            feat = "ngram{}{}^{}={}".format(num_words_before, num_words_after,
                                            self.factor, ' '.join(ngram))
            vector.add_source_feature(feat.lower(), self.weight)
