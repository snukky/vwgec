import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from utils import cmd
from logger import log


class VWPredictor(object):
    def __init__(self, vw):
        self.vw = vw

    def run(self, model, data, predictions, options=" -q st"):
        if not os.path.exists(model):
            log.error("model does not exist: {}".format(model))
        if not os.path.exists(data):
            log.error("data file does not exist: {}".format(data))

        log.info("running VW: {}".format(model))
        cmd.run("{vw}/vowpalwabbit/vw -t -i {model} -d {data} -c {options} -r {pred}"
            .format(
                vw=self.vw,
                model=model,
                data=data,
                options=options,
                pred=predictions))
