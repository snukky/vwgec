import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from gecvw.settings import config
from taggers.pos_tagger import StanfordPOSTagger
from taggers.wc_tagger import WordClassTagger
from utils import cmd
from logger import log


class FACTORS():
    TXT = 0
    POS = 1
    WC = 2

    ALL = {1: 'pos', 2: 'wc'}

    def __iter__(self):
        return ALL.iteritems()

    @staticmethod
    def names():
        return set(FACTORS.ALL.values())


def factorize_file(txt_file, factors=[], is_parallel=None):
    if not factors:
        return {}
    log.info("Factorize file {}".format(txt_file))

    if is_parallel is None:
        is_parallel = cmd.is_parallel(txt_file)

    in_file = txt_file
    if is_parallel:
        in_file = os.path.splitext(txt_file)[0] + '.in'
        cmd.cut(txt_file, in_file, field=0)

    files = {}
    for factor in factors:
        if factor not in FACTORS.names():
            log.warn("Unrecognized factor '{}'".format(factor))
        if 'pos' == factor:
            files['pos'] = StanfordPOSTagger().tag_file(in_file)
        if 'wc' == factor:
            files['wc'] = WordClassTagger().tag_file(in_file)

    return files
