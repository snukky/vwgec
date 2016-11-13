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

    threshold = gecvw.run_grid_search(config, None, args.pred)
    print threshold


def parse_user_args():
    parser = argparse.ArgumentParser()

    # parser.add_argument('--m2', required=True,
        # help="")

    # parser.add_argument('-c', '--cwords', required=True,
        # help="file with confusion words")
    parser.add_argument('-p', '--pred', type=argparse.FileType('r'), required=True,
        help="confusion words")
    parser.add_argument('-f', '--config', required=True,
        help="configuration file")

    return parser.parse_args()


if __name__ == '__main__':
    main()

