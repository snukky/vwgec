import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from features.base_feature import BaseFeature
from logger import log


class SourceWordFeature(BaseFeature):
    def extract(self, cword, csets, sentence, vector):
        vector.add_source_feature("err={}".format(cword.err.lower()))
