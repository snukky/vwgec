#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import linecache

from csets.cset import CSetPair
from csets.cword_reader import CWordReader
from feats.feature_extractor import FeatureExtractor

from config import load_config


def main():
    args = parse_user_args()
    config = load_config(args.config)

    reader = CWordReader(args.cwords)
    extractor = FeatureExtractor(
        CSetPair(config['source-cset'], config['target-cset']),
        config['features'])

    for sid, cword in reader:
        sentence = linecache.getline(args.input,
                                     sid + 1).strip().split("\t")[0].split()
        feat_str = extractor.extract_features(cword, sentence)
        args.output.write(feat_str)


def parse_user_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'cwords',
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help="Confusion words file")
    parser.add_argument(
        'output',
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdout,
        help="Output file")

    parser.add_argument('-i', '--input', required=True, help="Input sentences")
    parser.add_argument(
        '-f', '--config', required=True, help="Configuration file")

    return parser.parse_args()


if __name__ == '__main__':
    main()
