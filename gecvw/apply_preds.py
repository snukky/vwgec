#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import gecvw
import gecvw.prediction


def main():
    args = parse_user_args()
    gecvw.load_config(args.config)
    gecvw.prediction.apply_predictions(args.input, args.output, args.cword,
                                       args.pred)


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

    return parser.parse_args()


if __name__ == '__main__':
    main()
