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

from logger import log


def load_config(config_file):
    with open(config_file, 'r') as config_io:
        try:
            return yaml.load(config_io)
        except yaml.YAMLError as ex:
            print(ex)
    return None


def extract_features(config, input, output, cwords, train=False):
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


def apply_predictions(config, input, output, cwords, preds):
    pred_iter = PredictionIterator(
        input, cwords, preds, cset=CSet(config['target-cset']))
    formatter = OutputFormatter(output)

    for sid, sentence, preds in pred_iter:
        formatter.format(sid, sentence, preds)


def run_grid_search(config, cwords, preds):
    evaluator = M2Evaluator(None, cwords)
    searcher = GridSearch(evaluator, preds)
    return searcher.run()
