import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from collections import Iterator
from utils.softmax import softmax

from logger import log


class LDFIterator(Iterator):
    def __init__(self, stream, cset=None, sort=True):
        self.stream = stream
        self.labels = None
        if cset:
            log.debug(cset)
            self.labels = cset.tolist()
            log.debug("Labels: {}".format(self.labels))
        self.sort = sort

    def next(self):
        values = []
        while True:
            line = self.stream.next().strip()
            if not line:
                break
            values.append(self.__parse_line(line))
        # log.debug("Predictions: {}".format(values))
        labels = self.labels if self.labels else range(len(values))
        probs = softmax([-v for v in values])
        # log.debug("Probabilities: {}".format(probs))
        preds = zip(labels, probs)
        if self.sort:
            preds.sort(key=lambda x: x[1], reverse=True)
        return preds

    def __parse_line(self, line):
        return float(line.rstrip().rsplit(":", 1)[-1])


