import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from gecvw.settings import config

from csets.cset import CSetPair
from csets.cword_finder import CWordFinder
from csets.cword_reader import CWordReader

from features.feature_extractor import FeatureExtractor

from logger import log


def extract_features(txt_io, feat_io, cword_io, train=False):
    log.info("Extract features from {}".format(txt_io.name))

    csets = CSetPair(config['source-cset'], config['target-cset'])
    finder = CWordFinder(csets, train)
    extractor = FeatureExtractor(csets, config['features'], config['costs'])
    reader = CWordReader(cword_io)

    count = 0
    for sid, line in enumerate(txt_io):
        for cword in finder.find_confusion_words(line):

            sentence = line.split("\t", 1)[0].split()
            feat_str = extractor.extract_features(cword, sentence)
            feat_io.write(feat_str)

            reader.format(sid, cword)
            count += 1

    log.info("Found {} confusion words".format(count))
