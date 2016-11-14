import os
import shutil

from logger import log


def run(cmd):
    log.debug(cmd)
    return os.popen(cmd).read()
