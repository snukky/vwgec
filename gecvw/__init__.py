import os
import sys
import yaml

sys.path.insert(0, os.path.dirname(__file__))

from csets.cset import CSet
from csets.cset import CSetPair
from csets.cword_finder import CWordFinder
from csets.cword_reader import CWordReader

from features.feature_extractor import FeatureExtractor

from prediction.prediction_iterator import PredictionIterator
from prediction.output_formatter import OutputFormatter

from evaluation.grid_search import GridSearch
from evaluation.m2 import M2Evaluator

from settings import config
from logger import log


def load_config(config_file, updated_configs={}):
    settings.config.load_config(config_file, updated_configs)


# def find_confusion_words(input, cwords, train=False):
    # log.info("Find confusion words in {}".format(input.name))

    # csets = CSetPair(config['source-cset'], config['target-cset'])
    # finder = CWordFinder(csets, train)
    # reader = CWordReader(cwords)

    # count = 0
    # for sid, line in enumerate(input):
        # for cword in finder.find_confusion_words(line):
            # reader.format(sid, cword)
            # count += 1

    # log.info("Found {} confusion words".format(count))


def extract_features(input, output, cwords, train=False):
    log.info("Extract features from {}".format(input.name))

    csets = CSetPair(config['source-cset'], config['target-cset'])
    finder = CWordFinder(csets, train)
    extractor = FeatureExtractor(csets, config['features'], config['costs'])
    reader = CWordReader(cwords)

    count = 0
    for sid, line in enumerate(input):
        for cword in finder.find_confusion_words(line):

            sentence = line.split("\t", 1)[0].split()
            feat_str = extractor.extract_features(cword, sentence)
            output.write(feat_str)

            reader.format(sid, cword)
            count += 1

    log.info("Found {} confusion words".format(count))


def apply_predictions(input, output, cwords, preds):
    pred_iter = PredictionIterator(
        input, cwords, preds, cset=CSet(config['target-cset']))
    formatter = OutputFormatter(output)

    for sid, sentence, preds in pred_iter:
        formatter.format(sid, sentence, preds)


def run_grid_search(m2_file, cwords, preds):
    evaluator = M2Evaluator(m2_file, cwords, preds)
    searcher = GridSearch(evaluator, preds)
    return searcher.run()
