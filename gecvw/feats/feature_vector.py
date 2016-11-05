import os
import sys

from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))

from logger import log


class FeatureVector(object):
    def __init__(self, tgt_cset, costs=[]):
        self.cset = tgt_cset
        self.costs = costs
        self.src_feats = []
        self.tgt_feats = {cw: list() for cw in self.cset}

    def add_source_feature(self, feature):
        self.src_feats.append(self.escape_special_chars(feature))

    def add_target_feature(self, tgt, feature):
        self.tgt_feats[tgt].append(self.escape_special_chars(feature))

    def format(self, source, target):
        text = "shared |s {} {}\n".format(source, ' '.join(self.src_feats))
        for label, features in self.tgt_feats.iteritems():
            cost = 0.0 if label == target else 1.0
            text += "1111:{} |t {} {}\n".format(cost, label,
                                                ' '.join(features))
        self.src_feats = []
        self.tgt_feats = {cw: list() for cw in self.cset}
        return text + "\n"

    def escape_special_chars(self, text):
        return text.replace(' ', '_').replace(':', ';').replace('|', '/')
