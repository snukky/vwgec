import os
import sys
import re

sys.path.insert(0, os.path.dirname(__file__))

from prediction.base_formatter import BaseFormatter
from utils.softmax import softmax
from logger import log


class PLFFormatter(BaseFormatter):
    def __init__(self, *args, **kwargs):
        super(PLFFormatter, self).__init__(*args, **kwargs)
        self.with_comma = True

    def format(self, sentence, all_preds=None):
        edges = []
        tokens = sentence.split()
        c = 0

        if all_preds is None:
            all_preds = []

        for i, tok in enumerate(tokens):
            cur_preds = filter(lambda p: p[0].pos[0] == i, all_preds)

            # no predictions for i-th token
            if not cur_preds or i == len(tokens) - 1:
                edges.append("('{}',1.0,1)".format(tok))
            # predictions for i-th token
            else:
                for cword, preds in cur_preds:
                    nexttok = tokens[cword.pos[1]]
                    alts = self.format_alternatives(cword, preds, nexttok)

                    if alts:
                        edges.append(alts)
                        i, j = cword.pos
                        if i == j:
                            edges.append("('{}',1.0,1)".format(tok))
                        c += 1
                    else:
                        edges.append("('{}',1.0,1)".format(tok))

        return self.__plf_line(edges), c

    def __plf_line(self, edges):
        output = ''
        if self.with_comma:
            output = ''.join(["({},),".format(e) for e in edges])
        else:
            output = ','.join(["({})".format(e) for e in edges])
        return '(' + output.replace("\\", "\\\\") + ')'

    def format_alternatives(self, cword, preds, nexttok):
        pred = self.predicted_word(cword, preds)
        alts = []

        if pred.lower() != cword.err.lower():
            # Use the predicted probability for both source/original word and
            # prediction, next makes then true probabilities with softmax
            # function.
            prob_err = dict(preds)[cword.src]
            prob_pred = preds[0][1]
            prob_err, prob_pred = softmax([prob_err, prob_pred])
            # Alternatively, use the sum of probabilities for confusion words
            # differ from source/original word as the probability for
            # prediction.
            # prob_pred = 1.0 - prob_err

            alts.append(self.__plf_alternative(cword.err, nexttok, prob_err))
            alts.append(self.__plf_alternative(pred, nexttok, prob_pred))

        return ','.join(alts)

    def __plf_alternative(self, tok, nexttok, prob):
        if tok == '' or tok == '<null>':
            text = nexttok
            size = 2
        else:
            text = tok
            size = 1
        if prob == 1.0:
            return "('{}',1.0,{})".format(text, size)
        return "('{}',{:.4f},{})".format(text, prob, size)
