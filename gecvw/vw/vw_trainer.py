import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from utils import cmd
from logger import log


class VWTrainer(object):
    def __init__(self, vw):
        self.vw = vw

    def train(self, model, data, options=" --csoaa_ldf m -q st"):
        if os.path.exists(model):
            log.warn("model already exists: {}".format(model))
        if not os.path.exists(data):
            log.error("data file does not exist: {}".format(data))

        log.info("training VW: {}".format(model))
        cmd.run("{vw}/vowpalwabbit/vw -f {model} -d {data} -c {options}" \
            .format(vw=self.vw, model=model, data=data, options=options))
