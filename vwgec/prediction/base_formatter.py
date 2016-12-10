import os
import sys
import re

sys.path.insert(0, os.path.dirname(__file__))

from csets.cset import CSetPair
from logger import log


class BaseFormatter(object):
    def __init__(self, threshold=0.0, restore_case=True, debug=False):
        self.threshold = threshold
        self.restore_case = restore_case
        self.debug = debug

    def format(self, sentence, all_preds):
        raise NotImplementedError()

    def predicted_word(self, cword, preds):
        # predictions are already sorted from best to worse
        pred_cw, conf = preds[0]
        if (pred_cw == cword.src) or (self.threshold and
                                      conf < self.threshold):
            return cword.err
        # TODO: restore case?
        return CSetPair.construct_correction(cword.err, cword.src, pred_cw)

    def debug_input(self, text, n=0):
        tokens = text.split()
        debug_toks = [str(elem)
                      for pair in zip(tokens, xrange(len(tokens)))
                      for elem in reversed(pair)]
        return "{}: {}".format(n, '_'.join(debug_toks))

    def debug_preds(self, cword, preds, pred):
        nice_preds = " ".join("{}={:.3f}".format(e[0], e[1]) for e in preds)
        debug = "  predictions: {}".format(nice_preds)
        debug += "  {} {} -> {}".format(cword.pos, cword.err, pred)
        return debug

