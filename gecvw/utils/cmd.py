import os
import shutil

from config import SCRIPTS_DIR
from logger import log


def run(cmd):
    log.debug(cmd)
    return os.popen(cmd).read()


def parallelize_m2(m2_file, text_file):
    run("perl {scripts}/make_parallel.perl < {m2} > {txt}" \
        .format(scripts=SCRIPTS_DIR, m2=m2_file, txt=txt_file))
