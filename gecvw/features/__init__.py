import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from gecvw.settings import config

from csets.cset import CSetPair
from csets.cword_finder import CWordFinder
from csets.cword_reader import CWordReader

from features.feature_extractor import FeatureExtractor

from taggers.pos_tagger import StanfordPOSTagger
from taggers.wc_tagger import WordClassTagger
from taggers import FACTORS

from logger import log


def extract_features(txt_io, feat_io, cword_io, train=False, factor_files={}):
    log.info("Extract features from {}".format(txt_io.name))

    csets = CSetPair(config['source-cset'], config['target-cset'])
    extractor = FeatureExtractor(csets, config['features'], config['costs'])

    factors = {}
    for factor_id in extractor.required_factors():
        if factor_id == FACTORS.TXT:
            continue

        factor_name = FACTORS.ALL[factor_id]
        if factor_name not in factor_files:
            log.error("File with '{}' factor not provided".format(factor_name))
            exit(1)
        else:
            factor_file = factor_files[factor_name]
            log.info("'{}' factor file: {}".format(factor_name, factor_file))
            factors[factor_name] = open(factor_file)

    finder = CWordFinder(csets, train)
    reader = CWordReader(cword_io)

    count = 0
    for sid, line in enumerate(txt_io):

        txt_toks = line.split("\t", 1)[0].split()
        pos_toks = None
        if 'pos' in factors:
            pos_toks = factors['pos'].next().strip().split()
        awc_toks = None
        if 'wc' in factors:
            awc_toks = factors['wc'].next().strip().split()
        sentence = [txt_toks, pos_toks, awc_toks]

        for cword in finder.find_confusion_words(line):
            feat_str = extractor.extract_features(cword, sentence)
            feat_io.write(feat_str)

            reader.format(sid, cword)
            count += 1

    for factor in factors.values():
        factor.close()

    log.info("Found {} confusion words".format(count))
