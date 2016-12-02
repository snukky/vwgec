import os

from logger import log
from factors import FACTORS


def each_factorized_input(input_io, factor_files):
    factors = {fn: open(ff)
               for fn, ff in factor_files.iteritems() if ff is not None}

    for sid, line in enumerate(input_io):
        txt_toks = line.split("\t", 1)[0].split()
        pos_toks = None
        if 'pos' in factors:
            pos_toks = factors['pos'].next().strip().split()
        awc_toks = None
        if 'wc' in factors:
            awc_toks = factors['wc'].next().strip().split()

        yield sid, line, (txt_toks, pos_toks, awc_toks)

    for ff in factors.values():
        ff.close()
