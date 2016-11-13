import os
import shutil

from config import SCRIPTS_DIR
from logger import log


def run(cmd):
    log.debug(cmd)
    return os.popen(cmd).read()
