#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import vwgec
from vwgec.csets.cmatrix import CMatrixBuilder


def main():
    args = parse_user_args()

    cmatrix = CMatrixBuilder().build(args.cwords, args.min_err_count,
                                     args.min_cor_count)
    if args.output:
        cmatrix.save(args.output)
    else:
        for cor, err, count, prob in cmatrix.sorted_edits():
            print "{}\t{}\t{}\t{}".format(cor, err, count, prob)


def parse_user_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('cwords', nargs='?', type=argparse.FileType('r'),
        default=sys.stdin, help="confusion words")
    parser.add_argument('-o', '--output', help="output matrix")
    parser.add_argument("-e", "--min-err-count", type=int, default=3)
    parser.add_argument("-c", "--min-cor-count", type=int, default=5)

    return parser.parse_args()


if __name__ == '__main__':
    main()
