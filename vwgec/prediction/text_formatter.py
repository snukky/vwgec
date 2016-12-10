import os
import sys
import re

sys.path.insert(0, os.path.dirname(__file__))

from prediction.base_formatter import BaseFormatter
from utils.letter_case import restore_sentence_case
from logger import log


class TextFormatter(BaseFormatter):
    def __init__(self, *args, **kwargs):
        super(TextFormatter, self).__init__(*args, **kwargs)

    def format(self, sentence, all_preds=None):
        if all_preds is None:
            return sentence
        tokens = sentence.split()
        debug = ""
        c = 0

        for cword, preds in all_preds:
            pred = self.predicted_word(cword, preds)
            if self.debug:
                debug += self.debug_preds(cword, preds, pred)

            if cword.err.lower() != pred.lower():
                i, j = cword.pos
                if i == j:
                    pred += ' ' + tokens[i]
                tokens[i] = pred
                c += 1

        new_sentence = re.sub(r'\s\s+', ' ', ' '.join(tokens))
        if self.restore_case and new_sentence != sentence:
            new_sentence = restore_sentence_case(new_sentence, sentence)

        if self.debug and c > 0:
            log.debug(debug)
        return (new_sentence, c)
