#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse

from csets.cset import CSet
from csets.cword_finder import CWordFinder
from csets.cword_reader import CWordReader


def main():
    args = parse_user_args()

    finder = CWordFinder(
        CSet(args.source_cset), CSet(args.target_cset), args.train)
    reader = CWordReader()

    for sid, line in enumerate(args.input):
        for cword_info in finder.find_confusion_words(line):
            line = reader.format_line(sid, cword_info)
            args.output.write(line + "\n")


def parse_user_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('input', nargs='?', type=argparse.FileType('r'),
        default=sys.stdin, help="Input sentences")
    parser.add_argument('output', nargs='?', type=argparse.FileType('r'),
        default=sys.stdout, help="Output file")

    parser.add_argument('-1', '--source-cset', required=True,
        help="Source confusion set")
    parser.add_argument('-2', '--target-cset', required=True,
        help="Target confusion set")

    parser.add_argument('-t', '--train', action='store_true',
        help="Train mode")

    return parser.parse_args()


if __name__ == '__main__':
    main()
