import os
import sys
import re

sys.path.insert(0, os.path.dirname(__file__))

from csets.cset import CSetPair
from utils.letter_case import restore_sentence_case
from logger import log


class OutputFormatter(object):
    def __init__(self, output, threshold=0.0, restore_case=True, debug=False):
        self.output = open(output, 'w')
        self.threshold = 0.0
        self.restore_case = restore_case
        self.debug = debug

    def format(self, n, sentence, preds):
        if not preds:
            self.output.write(sentence + "\n")
            return

        if self.debug:
            log.debug("apply predictions into {}: '{}'".format(n, sentence))
        new_sentence, _ = self.apply_predictions(sentence, preds)
        self.output.write(new_sentence + "\n")

    def apply_predictions(self, sentence, all_preds):
        tokens = sentence.split()
        c = 0

        for cword, preds in all_preds:
            pred = self.__predicted_word(cword, preds)

            if self.debug:
                log.debug("  {} {} -> {}".format(cword.pos, cword.err, pred))
                log.debug("  predictions: {}".format(preds))

            if cword.err.lower() != pred.lower():
                i, j = cword.pos
                if i == j:
                    pred += ' ' + tokens[i]
                tokens[i] = pred
                c += 1

        new_sentence = re.sub(r'\s\s+', ' ', ' '.join(tokens))

        if self.restore_case and new_sentence != sentence:
            new_sentence = restore_sentence_case(new_sentence, sentence)

        return (new_sentence, c)

    def __predicted_word(self, cword, preds):
        # predictions are already sorted from best to worse
        pred_cw, conf = preds[0]
        if (pred_cw == cword.src) or (self.threshold and conf < self.threshold):
            return cword.err
        # TODO: restore case?
        return CSetPair.construct_correction(cword.err, cword.src, pred_cw)

    def __show_text_debug(self, text, n=0):
        tokens = text.split()
        debug_toks = [str(elem)
                      for pair in zip(tokens, xrange(len(tokens)))
                      for elem in reversed(pair)]
        log.debug("{}: {}".format(n, '_'.join(debug_toks)))
