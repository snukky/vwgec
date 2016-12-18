import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from vwgec.settings import config

from csets.cset import CSetPair
from csets.cword_finder import CWordFinder
from csets.null_finder import NullFinder
from csets.cword_reader import CWordReader
from csets.cmatrix import CMatrixBuilder

from utils.input import each_factorized_input

from logger import log


def find_confusion_words(txt_io,
                         cword_io,
                         train=False,
                         factor_files={},
                         nulls=True):
    log.info("Find confusion words in {}".format(txt_io.name))

    csets = CSetPair(config['source-cset'], config['target-cset'])
    finder = CWordFinder(csets, train)
    if nulls and config['nulls-ngrams']:
        null_finder = NullFinder(csets.src, config['nulls-ngrams'])
        finder.add_extra_finder(null_finder)
    else:
        finder.clear_extra_finders()
    reader = CWordReader(cword_io)

    count = 0
    for sid, line, fact_sent in each_factorized_input(txt_io, factor_files):
        for cword in finder.find_confusion_words(line, fact_sent):
            reader.format(sid, cword)
            count += 1

    log.info("Found {} confusion words".format(count))


def build_cmatrix(cword_io, matrix_io):
    cmatrix = CMatrixBuilder().build(cword_io)

    matrix_io.write(cmatrix.tabulate(show='prob') + "\n\n")
    matrix_io.write(cmatrix.tabulate(show='count') + "\n\n")
    matrix_io.write(cmatrix.stats() + "\n")

    for cor, err, count, prob in cmatrix.sorted_edits():
        matrix_io.write("{}\t{}\t{}\t{}\n".format(cor, err, count, prob))
