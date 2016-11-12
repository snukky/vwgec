#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import gecvw


def main():
    args = parse_user_args()
    config = gecvw.load_config(args.config)
    gecvw.apply_predictions(config, args.input, args.output, args.cwords, args.preds)


def parse_user_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('input', nargs='?', type=argparse.FileType('r'),
        default=sys.stdin, help="input sentences")
    parser.add_argument('output', nargs='?', type=argparse.FileType('r'),
        default=sys.stdout, help="output file")

    parser.add_argument('-p', '--preds', required=True,
        help="prediction file")
    parser.add_argument('-c', '--cwords', required=True,
        help="confusion words file")
    parser.add_argument('-f', '--config', required=True,
        help="configuration file")

    return parser.parse_args()


if __name__ == '__main__':
    main()
