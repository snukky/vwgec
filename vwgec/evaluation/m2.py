import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from vwgec.settings import config
from prediction.prediction_reader import PredictionReader
from prediction.output_formatter import OutputFormatter

from evaluation import maxmatch
from utils import cmd

from settings import SCRIPTS_DIR
from logger import log


class M2Evaluator(object):
    def __init__(self,
                 m2_file,
                 cword_file,
                 pred_file,
                 txt_file=None,
                 work_dir=None):
        self.i = 0
        self.m2_file = m2_file
        self.cword_file = cword_file
        self.pred_file = pred_file
        self.cset = config['target-cset']

        self.work_dir = work_dir or '.'
        if not os.path.exists(self.work_dir):
            raise Exception("Directory does not exist: {}".format(
                self.work_dir))

        self.txt_file = txt_file or m2_file + '.txt.tmp'
        maxmatch.parallelize_m2(self.m2_file, self.txt_file)

    def run(self, thr):
        out = self.work_dir + "/thr{}.out".format(thr)
        self.apply_predictions(thr, self.txt_file, out, self.cword_file,
                               self.pred_file)
        scores = self.evaluate(out, self.m2_file)
        log.info("M2 fscore: {}".format(scores))
        return scores

    def apply_predictions(self, threshold, txt_file, out_file, cword_file, pred_file):
        pred_iter = PredictionReader(
            txt_file, cword_file, pred_file, cset=self.cset, open_files=True)

        out_io = open(out_file, 'w')
        formatter = OutputFormatter(out_io, threshold)
        for sid, sentence, preds in pred_iter:
            formatter.format(sid, sentence, preds)
        out_io.close()

    def evaluate(self, out_file, m2_file):
        num_of_lines = cmd.wc(out_file)
        with open(m2_file) as m2_io:
            num_of_sents = sum(1 for line in m2_io if line.startswith("S "))

        if num_of_lines != num_of_sents:
            log.error("Different number of sentences between text and M2 file:"
                      " {} != {}".format(num_of_lines, num_of_sents))

        scores = maxmatch.evaluate_m2(out_file, m2_file)

        # Scores includes precision, recall, and F-score. We want to have
        # F-score as main evaluation metric.
        return scores[2], scores[0], scores[1]
