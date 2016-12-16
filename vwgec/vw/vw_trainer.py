import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from vwgec.settings import config
from utils import cmd
from logger import log


class VWTrainer(object):
    DEFAULT_OPTIONS = " --csoaa_ldf mc -q st -b 26 --hash all --noconstant --loss_function logistic"

    def __init__(self, vw=None):
        self.vw = vw or config['vowpal-wabbit']

    def train(self, model, data):
        if os.path.exists(model):
            log.warn("model already exists: {}".format(model))
        if not os.path.exists(data):
            log.error("data file does not exist: {}".format(data))

        options = (config['vw-options'] or "") + VWTrainer.DEFAULT_OPTIONS

        log.info("train VW: {}".format(model))
        cmd.run("{vw}/vowpalwabbit/vw -f {model} -d {data} -c {options}" \
            .format(vw=self.vw, model=model, data=data, options=options))
