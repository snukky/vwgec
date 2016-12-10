import os
import sys
import re

sys.path.insert(0, os.path.dirname(__file__))

from csets.cset import CSetPair
from utils.letter_case import restore_sentence_case
from prediction.text_formatter import TextFormatter
from prediction.plf_formatter import PLFFormatter
from logger import log


class OutputFormatter(object):
    FORMATS = {
        'txt': TextFormatter,
        'plf': PLFFormatter,
    }

    def __init__(self,
                 output,
                 format='txt',
                 threshold=0.0,
                 restore_case=True,
                 debug=True):
        self.output = output
        if format not in OutputFormatter.FORMATS.keys():
            log.error("Output format '{}' not recognized".format(format))
        else:
            log.info("Use '{}' output format".format(format))
        self.formatter = OutputFormatter.FORMATS[format](threshold,
                                                         restore_case, debug)

    def format(self, n, sentence, preds):
        new_sentence, _ = self.formatter.format(sentence, preds)
        self.output.write(new_sentence + "\n")
