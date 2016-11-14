#!/usr/bin/python

import os
import sys
import gzip
import io

sys.path.insert(0, os.path.dirname(__file__))

from settings import config
from logger import log


class WordClassTagger:
    def __init__(self, dictionary=None):
        self.unknown_wc = '?'
        self.dictionary = dictionary or config['word-classes']
        self.__load_dictionary()

    def tag(self, tokens):
        return [self.dic.get(tok.lower(), self.unknown_wc) for tok in tokens]

    def tag_file(self, tok_file, awc_file=None, lazy=True):
        if awc_file is None:
            awc_file = tok_file + '.awc'

        if lazy and os.path.exists(awc_file):
            log.info("Tagging skipped because file {} exists".format(awc_file))
            return awc_file

        log.info("Tagging file {}".format(tok_file))
        with open(tok_file) as tok_io, open(awc_file, 'w+') as awc_io:
            for line in tok_io:
                awc_io.write(' '.join(self.tag(line.strip().split())) + "\n")

        return awc_file

    def __load_dictionary(self):
        log.info("Load dictionary {}...".format(self.dictionary))
        self.dic = {}

        reader = gzip if self.dictionary.endswith('.gz') else io
        with reader.open(self.dictionary) as f:
            for line in f:
                word, tag = line.split()[:2]
                self.dic[word] = tag
                if word.find('&apos;') != -1:
                    self.dic[word.replace('&apos;', "'")] = tag
                if word.find('&quot;') != -1:
                    self.dic[word.replace('&quot;', '"')] = tag


if __name__ == '__main__':
    tagger = WordClassTagger()
    for line in sys.stdin:
        print ' '.join(tagger.tag(line.strip().split()))
