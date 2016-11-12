#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import linecache

from csets.cset import CSetPair
from csets.cword_finder import CWordFinder
from feats.feature_extractor import FeatureExtractor
from csets.cword_reader import CWordReader

from config import load_config
from logger import log


def main():
    args = parse_user_args()
    config = load_config(args.config)

    csets = CSetPair(
        args.source_cset or config['source-cset'],
        args.target_cset or config['target-cset'])

    finder = CWordFinder(csets, args.train)
    extractor = FeatureExtractor(csets, config['features'], config['costs'])
    reader = CWordReader(args.cwords)

    count = 0
    for sid, line in enumerate(args.input):
        for cword in finder.find_confusion_words(line):

            sentence = line.split("\t", 1)[0].split()
            feat_str = extractor.extract_features(cword, sentence)
            args.output.write(feat_str)

            reader.format(sid, cword)
            count += 1

    log.info("Found {} confusion words".format(count))


def parse_user_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('input', nargs='?', type=argparse.FileType('r'),
        default=sys.stdin, help="input sentences")
    parser.add_argument('output', nargs='?', type=argparse.FileType('r'),
        default=sys.stdout, help="output features")

    parser.add_argument('-1', '--source-cset',
        help="source confusion set")
    parser.add_argument('-2', '--target-cset',
        help="target confusion set")

    parser.add_argument('-c', '--cwords', type=argparse.FileType('w'),
        required=True, help="file to store found confusion words")
    parser.add_argument('-f', '--config', required=True,
        help="configuration file")
    parser.add_argument('-t', '--train', action='store_true',
        help="turn on train mode")

    return parser.parse_args()


if __name__ == '__main__':
    main()
