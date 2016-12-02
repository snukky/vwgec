import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from vwgec.settings import config
from csets.cset import CSetPair
from csets.cword_finder import CWordFinder
from csets.cword_reader import CWordReader
from csets.null_finder import NullFinder
from features.feature_extractor import FeatureExtractor
from factors import FACTORS
from utils.input import each_factorized_input
from logger import log


def extract_features(txt_io, feat_io, cword_io, train=False, factor_files={}):
    log.info("Extract features from {}".format(txt_io.name))

    csets = CSetPair(config['source-cset'], config['target-cset'])
    extractor = FeatureExtractor(csets, config['features'], config['costs'])

    check_factor_requirements(extractor.required_factors(), factor_files)

    finder = CWordFinder(csets, train)
    if config['null-ngrams']:
        null_finder = NullFinder(csets.src, config['null-ngrams'])
        finder.add_extra_finder(null_finder)
    reader = CWordReader(cword_io)

    count = 0
    for sid, line, fact_sent in each_factorized_input(txt_io, factor_files):
        log.debug("Find confusion words in #{} sentence".format(sid))

        for cword in finder.find_confusion_words(line, fact_sent):
            feat_str = extractor.extract_features(cword, fact_sent)
            feat_io.write(feat_str)

            reader.format(sid, cword)
            count += 1

    log.info("Found {} confusion words".format(count))


def check_factor_requirements(required_factors, provided_factors):
    for factor_id in required_factors:
        if factor_id == FACTORS.TXT:
            continue

        factor_name = FACTORS.NUMS[factor_id]
        if factor_name not in provided_factors:
            log.error("File with '{}' factor not provided".format(factor_name))
            exit(1)
            return False
        else:
            factor_file = provided_factors[factor_name]
            log.info("'{}' factor file: {}".format(factor_name, factor_file))
    return True
