#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse

import csets


def main():
    args = parse_user_args()


def parse_user_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'input',
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help="Input sentences")
    parser.add_argument('-f', '--config', help="Configuration file")

    return parser.parse_args()


if __name__ == '__main__':
    main()
