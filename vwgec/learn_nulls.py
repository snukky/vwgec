#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import vwgec
from vwgec.csets.cset import CSet
from vwgec.csets.null_ngrams import NullNGramsFinder
from vwgec.utils import cmd


def main():
    args = parse_user_args()
    vwgec.load_config(args.config, {'source-cset': args.confusion_set,
                                    'target-cset': args.confusion_set})

    if args.input_factor:
        factor_file = args.input_factor
    else:
        factor_file = args.input + '.in'
        cmd.cut(args.input, factor_file, field=0)

    nulls = NullNGramsFinder(args.left_context, args.right_context,
                             args.min_count)
    nulls.find_ngrams(args.input, factor_file, args.output, factor=args.factor)


def parse_user_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('input', help="input sentences")
    parser.add_argument('output', help="output features")

    parser.add_argument('-i', '--input-factor',
        help="input factor file")
    parser.add_argument('-c', '--confusion-set',
        help="source confusion set")
    parser.add_argument('-f', '--config', required=True,
        help="configuration file")

    train = parser.add_argument_group("training arguments")
    train.add_argument('--factor', default='tok',
        help="factor, default 'tok'")
    train.add_argument('--left-context', type=int, default=1,
        help="size of left context")
    train.add_argument('--right-context', type=int, default=3,
        help="size of right context")
    train.add_argument('--min-count', type=int, default=5,
        help="minimum frequency of n-grams")

    return parser.parse_args()


if __name__ == '__main__':
    main()
