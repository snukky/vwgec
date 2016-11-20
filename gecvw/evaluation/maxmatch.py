from utils import cmd
from settings import SCRIPTS_DIR


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

    # Scorer is run by system shell because of the bug inside the scorer
    # script which cause propagation of forked threads to this script.
    result = cmd.run(
        "python {scripts}/m2scorer_fork --forks {threads} {txt} {m2}" \
            .format(scripts=SCRIPTS_DIR, threads=4, txt=out_file, m2=m2_file))

    if log_file:
        with open(log_file, 'w') as log_io:
            log_io.write(result)

    # Currently I'm using Marcin's C++ implementation of m2scorer.
    # result = cmd.run("{scorer} --candidate {txt} --reference {m2}" \
    # .format(scorer=config.TOOLS.M2SCORER_CPP, txt=text_file, m2=m2_file))

    return tuple(
        float(line.rsplit(' ', 1)[-1]) for line in result.strip().split("\n"))
