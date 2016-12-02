#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(__file__))

from vw.vw_trainer import VWTrainer
from config import load_config


def main():
    args = parse_user_args()
    config = load_config(args.config)

    trainer = VWTrainer(config['vowpalwabbit'])
    trainer.train(config['model'], args.data)


def parse_user_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--data', required=True,
        help="Feature data file")
    parser.add_argument('-f', '--config', required=True,
        help="Configuration file")

    return parser.parse_args()


if __name__ == '__main__':
    main()
