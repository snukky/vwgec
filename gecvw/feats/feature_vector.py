import os
import sys

from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))

from logger import log

DEFAULT_COSTS = {'aaa': 0.0, 'aab': 1.0, 'abb': 0.0, 'aba': 4.0, 'abc': 1.0}


class FeatureVector(object):
    def __init__(self, tgt_cset, costs={}):
        self.cset = tgt_cset
        self.costs = costs or DEFAULT_COSTS
        self.src_feats = []
        self.tgt_feats = {cw: list() for cw in self.cset}

    def add_source_feature(self, feature):
        self.src_feats.append(self.escape_special_chars(feature))

    def add_target_feature(self, tgt, feature):
        self.tgt_feats[tgt].append(self.escape_special_chars(feature))

    def format(self, source, target):
        text = "shared |s {} {}\n".format(source, ' '.join(self.src_feats))
        for candidate, features in self.tgt_feats.iteritems():
            cost = self.get_cost(source, target, candidate)
            text += "1111:{} |t {} {}\n".format(cost, candidate,
                                                ' '.join(features))
        self.src_feats = []
        self.tgt_feats = {cw: list() for cw in self.cset}
        return text + "\n"

    def escape_special_chars(self, text):
        return text.replace(' ', '_').replace(':', ';').replace('|', '/')

    def get_cost(self, source, target, candidate):
        is_correct = candidate == target
        if source == target:
            return self.costs['aaa'] if is_correct else self.costs['aab']
        elif is_correct:
            return self.costs['abb']
        elif source == candidate:
            return self.costs['aba']
        return self.costs['abc']
