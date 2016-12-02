import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from vwgec.settings import config

from csets.cset import CSetPair
from csets.cword_finder import CWordFinder
from csets.null_finder import NullFinder
from csets.cword_reader import CWordReader

from utils.input import each_factorized_input

from logger import log


def find_confusion_words(txt_io, cword_io, train=False, factor_files={}):
    log.info("Find confusion words in {}".format(txt_io.name))

    csets = CSetPair(config['source-cset'], config['target-cset'])
    finder = CWordFinder(csets, train)
    if config['null-ngrams']:
        null_finder = NullFinder(csets.src, config['null-ngrams'])
        finder.add_extra_finder(null_finder)
    reader = CWordReader(cword_io)

    count = 0
    for sid, line, fact_sent in each_factorized_input(txt_io, factor_files):
        for cword in finder.find_confusion_words(line, fact_sent):
            reader.format(sid, cword)
            count += 1

    log.info("Found {} confusion words".format(count))
