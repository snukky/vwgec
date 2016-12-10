#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import vwgec
import vwgec.prediction


def main():
    args = parse_user_args()
    vwgec.load_config(args.config)
    vwgec.prediction.apply_predictions(args.input, args.output, args.cword,
                                       args.pred, args.output_format,
                                       args.threshold)


def parse_user_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('input', nargs='?', type=argparse.FileType('r'),
        default=sys.stdin, help="input sentences")
    parser.add_argument('output', nargs='?', type=argparse.FileType('w'),
        default=sys.stdout, help="output sentences")

    parser.add_argument('-c', '--cword', type=argparse.FileType('r'),
        required=True, help="file with confusion words")
    parser.add_argument('-p', '--pred', type=argparse.FileType('r'),
        required=True, help="file with predictions")
    parser.add_argument('-f', '--config', required=True,
        help="configuration file")
    parser.add_argument('-o', '--output-format', help="output format")
    parser.add_argument('-t', '--threshold', help="threshold confidence")

    return parser.parse_args()


if __name__ == '__main__':
    main()
