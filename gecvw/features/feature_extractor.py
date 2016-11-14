import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from features.feature_vector import FeatureVector
from features.base_feature import BaseFeature
from features.source import *
from features.target import *

from settings import config
from logger import log


class FeatureExtractor(object):
    def __init__(self, cset_pair, feats, costs=None):
        self.csets = cset_pair
        self.vector = FeatureVector(self.csets.tgt, costs)
        self.features = []
        self.factors = set()
        self.__initialize_features(feats)

    def extract_features(self, cword, sentence):
        log.debug("Extracting features for {}".format(cword))
        for feature in self.features:
            feature.extract(cword, self.csets, sentence, self.vector)
        return self.vector.format(cword.src, cword.tgt)

    def required_factors(self):
        return self.factors

    def __initialize_features(self, features):
        feature_classes = {cls.__name__: cls
                           for cls in self.__get_subclasses(BaseFeature)}

        for feat in features:
            if feat in feature_classes:
                kwargs = features[feat] or {}
                log.info("Initialize {} {}".format(feat, kwargs))
                obj = feature_classes[feat](**kwargs)
                self.features.append(obj)
                self.factors |= set([obj.factor])
            else:
                log.warn("Unrecognized feature: {}".format(feat))

    def __get_subclasses(self, cls):
        subclasses = []
        for subcls in cls.__subclasses__():
            subclasses.append(subcls)
            subclasses.extend(self.__get_subclasses(subcls))
        return subclasses
