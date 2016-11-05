#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse

from csets.cset import CSetPair
from csets.cword_finder import CWordFinder
from csets.cword_reader import CWordReader

from config import load_config


def main():
    args = parse_user_args()
    config = load_config(args.config)

    reader = CWordReader(args.output)
    finder = CWordFinder(
        CSetPair(config['source-cset'], config['target-cset']), args.train)

    for sid, line in enumerate(args.input):
        for cword in finder.find_confusion_words(line):
            reader.format(sid, cword)


def parse_user_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('input', nargs='?', type=argparse.FileType('r'),
        default=sys.stdin, help="Input sentences")
    parser.add_argument('output', nargs='?', type=argparse.FileType('r'),
        default=sys.stdout, help="Output file")

    # parser.add_argument('-1', '--source-cset', required=True,
    # help="Source confusion set")
    # parser.add_argument('-2', '--target-cset', required=True,
    # help="Target confusion set")

    parser.add_argument('-f', '--config', required=True,
        help="Configuration file")
    parser.add_argument('-t', '--train', action='store_true',
        help="Train mode")

    return parser.parse_args()


if __name__ == '__main__':
    main()
