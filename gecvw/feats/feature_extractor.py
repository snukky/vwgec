import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from feats.feature_vector import FeatureVector
from feats.base_feature import BaseFeature
from feats.source import *
from feats.target import *

from logger import log


class FeatureExtractor(object):
    def __init__(self, cset_pair, feats):
        self.csets = cset_pair
        self.features = []
        self.__initialize_features(feats)
        self.vector = FeatureVector(self.csets.tgt)

    def extract_features(self, cword, sentence):
        log.debug("extracting features for {}".format(cword))
        for feature in self.features:
            feature.extract(cword, self.csets, sentence, self.vector)
        return self.vector.format(cword.src, cword.tgt)

    def __initialize_features(self, features):
        for cls in self.__get_subclasses(BaseFeature):
            if cls.__name__ in features:
                kwargs = features[cls.__name__] or {}
                log.info("Initialize feature {}({})".format(cls.__name__,
                                                            kwargs or ''))
                self.features.append(cls(**kwargs))

        feature_set = set(f.__class__.__name__ for f in self.features)
        for feat in features:
            if feat not in feature_set:
                log.warn("Unrecognized feature: {}".format(feat))

    def __get_subclasses(self, cls):
        subclasses = []
        for subcls in cls.__subclasses__():
            subclasses.append(subcls)
            subclasses.extend(self.__get_subclasses(subcls))
        return subclasses
