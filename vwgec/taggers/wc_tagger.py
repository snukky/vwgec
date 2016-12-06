#!/usr/bin/python

import os
import sys
import gzip
import io
import cPickle as pickle

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from vwgec import settings
from vwgec.settings import config
from logger import log


class WordClassTagger:
    def __init__(self, dictionary=None):
        self.unknown_wc = '?'
        self.dictionary = dictionary or config['word-classes']
        self.nrm_quotes = False
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

    def save(self, dic_file):
        log.info("Save dictionary to {}".format(dic_file))
        with open(dic_file, 'wb') as dic_io:
            pickle.dump(self.dic, dic_io)

    def __load_dictionary(self):
        log.info("Load dictionary {}...".format(self.dictionary))
        self.dic = {}

        if self.dictionary.endswith('.pkl'):
            with open(self.dictionary, 'rb') as dic_io:
                self.dic = pickle.load(dic_io)
        else:
            reader = gzip if self.dictionary.endswith('.gz') else io
            with reader.open(self.dictionary) as dic_io:
                for line in dic_io:
                    word, tag = line.split()[:2]
                    self.dic[word] = tag

        if self.nrm_quotes:
            for word in self.dic:
                if word.find('&apos;') != -1:
                    self.dic[word.replace('&apos;', "'")] = self.dic[word]
                if word.find('&quot;') != -1:
                    self.dic[word.replace('&quot;', '"')] = self.dic[word]


if __name__ == '__main__':
    settings.config.load_config(sys.argv[1], {})
    tagger = WordClassTagger()
    for line in sys.stdin:
        print ' '.join(tagger.tag(line.strip().split()))
