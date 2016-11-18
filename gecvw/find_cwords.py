#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import gecvw
import gecvw.cset


def main():
    args = parse_user_args()
    gecvw.load_config(args.config, {'source-cset': args.source_cset,
                                    'target-cset': args.target_cset})
    gecvw.cset.find_confusion_words(args.input, args.output, args.train)


def parse_user_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('input', nargs='?', type=argparse.FileType('r'),
        default=sys.stdin, help="input sentences")
    parser.add_argument('output', nargs='?', type=argparse.FileType('w'),
        default=sys.stdout, help="output confusion words")

    parser.add_argument('-1', '--source-cset',
        help="source confusion set")
    parser.add_argument('-2', '--target-cset',
        help="target confusion set")

    parser.add_argument('-f', '--config', required=True,
        help="configuration file")
    parser.add_argument('-t', '--train', action='store_true',
        help="turn on train mode")

    return parser.parse_args()


if __name__ == '__main__':
    main()
