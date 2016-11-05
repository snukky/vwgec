import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from feats.base_feature import BaseFeature
from logger import log


class SourceNGramFeature(BaseFeature):
    def extract(self, cword, csets, sentence, vector):
        vector.add_source_feature("ngram={}".format(cword.err))
