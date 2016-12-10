#!/usr/bin/python

import os
import sys
import argparse
import nltk

nltk.data.path.append(os.path.expanduser("~/.local/share/nltk_data"))

parser = argparse.ArgumentParser(description="NLTK Tokenizer.")
parser.add_argument(
    "-l",
    "--language",
    default="english",
    help="set language, default: english")
parser.add_argument(
    "-s",
    "--split-sent",
    action="store_true",
    help="split line into sentences if necessary")
args = parser.parse_args()

if args.split_sent:
    segmentizer = nltk.data.load("tokenizers/punkt/{}.pickle" \
        .format(args.language))

    for line in sys.stdin:
        for sentence in segmentizer.tokenize(line.lstrip()):
            print " ".join(nltk.word_tokenize(sentence))

else:
    for line in sys.stdin:
        print " ".join(nltk.word_tokenize(line.strip()))
