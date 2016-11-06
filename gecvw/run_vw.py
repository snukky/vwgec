#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(__file__))

from vw.vw_predictor import VWPredictor
from config import load_config


def main():
    args = parse_user_args()
    config = load_config(args.config)

    vw = VWPredictor(config['vowpalwabbit'])
    vw.run(config['model'], args.data, args.prediction)


def parse_user_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--data', required=True,
        help="feature data file")
    parser.add_argument('-p', '--prediction', required=True,
        help="output file")
    parser.add_argument('-f', '--config', required=True,
        help="configuration file")

    return parser.parse_args()


if __name__ == '__main__':
    main()
