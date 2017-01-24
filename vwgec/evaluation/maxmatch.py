import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from vwgec.settings import config
from utils import cmd
from settings import SCRIPTS_DIR
from logger import log


class M2SCORER(object):
    MOSES = 'moses'
    OFFICIAL = 'official'


def parallelize_m2(m2_file, txt_file):
    cmd.run("perl {scripts}/make_parallel.perl < {m2} > {txt}" \
        .format(scripts=SCRIPTS_DIR, m2=m2_file, txt=txt_file))


def evaluate_m2(out_file, m2_file, log_file=None):
    num_of_lines = cmd.wc(out_file)
    with open(m2_file) as m2_io:
        num_of_sents = sum(1 for line in m2_io if line.startswith("S "))

    if num_of_lines != num_of_sents:
        log.error("Different number of sentences between text and M2 file:"
                  " {} != {}".format(num_of_lines, num_of_sents))

    if config['m2scorer'] == M2SCORER.MOSES:
    # C++ implementation of m2scorer from Moses.
        result = cmd.run("{moses}/bin/m2scorer --candidate {txt} --reference {m2}" \
            .format(moses=config['mosesdecoder'], txt=out_file, m2=m2_file))
    # Scorer is run by system shell because of the bug inside the scorer
    # script which cause propagation of forked threads to this script.
    else:
        result = cmd.run(
            "python {scripts}/m2scorer_fork --forks {threads} {txt} {m2}" \
            .format(scripts=SCRIPTS_DIR, threads=config['threads'] or 4,
                    txt=out_file, m2=m2_file))

    if log_file:
        with open(log_file, 'w') as log_io:
            log_io.write(result)

    return tuple(
        float(line.rsplit(' ', 1)[-1]) for line in result.strip().split("\n"))
