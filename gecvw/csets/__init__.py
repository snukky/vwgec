import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from gecvw.settings import config

from csets.cset import CSetPair
from csets.cword_finder import CWordFinder
from csets.cword_reader import CWordReader

from logger import log


def find_confusion_words(txt_io, cword_io, train=False):
    log.info("Find confusion words in {}".format(input.name))

    csets = CSetPair(config['source-cset'], config['target-cset'])
    finder = CWordFinder(csets, train)
    reader = CWordReader(cword_io)

    count = 0
    for sid, line in enumerate(txt_io):
        for cword in finder.find_confusion_words(line):
            reader.format(sid, cword)
            count += 1

    log.info("Found {} confusion words".format(count))
