from utils import cmd
from settings import SCRIPTS_DIR


def parallelize_m2(m2_file, txt_file):
    cmd.run("perl {scripts}/make_parallel.perl < {m2} > {txt}" \
        .format(scripts=SCRIPTS_DIR, m2=m2_file, txt=txt_file))
