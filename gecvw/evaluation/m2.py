import cmd

import utils.cmd
from settings import SCRIPTS_DIR
from logger import log


def parallelize_m2(m2_file, txt_file):
    cmd.run("perl {scripts}/make_parallel.perl < {m2} > {txt}" \
        .format(scripts=SCRIPTS_DIR, m2=m2_file, txt=txt_file))


class M2Evaluator(object):
    def __init__(self, m2_file, cword_file, txt_file=None):
        self.i = 0
        self.m2_file = m2_file
        self.cword_file = cword_file
        self.txt_file = txt_file

    def run(self, thr):
        self.i += 1
        log.info("M2 fscore: {}".format(1.0))
        return (1.0, self.i)

    def evaluate(self, txt_file, m2_file):
        num_of_lines = cmd.wc(txt_file)
        with open(m2_file) as m2_io:
            num_of_sents = sum(1 for line in m2_io if line.startswith("S "))

        if num_of_lines != num_of_sents:
            log.error("Different number of sentences in Text file and M2 file:"
                      " {} != {}".format(num_of_lines, num_of_sents))

        # Scorer is run by system shell because of the bug inside the scorer
        # script which cause the propagation of forked threads to this script.
        result = cmd.run(
            "python {scripts}/m2scorer_fork --forks {threads} {txt} {m2}" \
                .format(scripts=SCRIPTS_DIR, threads=4, txt=txt_file, m2=m2_file))

        # Currently I'm using Marcin's C++ implementation of m2scorer.
        # result = cmd.run("{scorer} --candidate {txt} --reference {m2}" \
        # .format(scorer=config.TOOLS.M2SCORER_CPP, txt=text_file, m2=m2_file))

        return tuple(
            float(line.rsplit(' ', 1)[-1])
            for line in result.strip().split("\n"))
