import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from collections import Iterator
from utils.softmax import softmax


class LDFIterator(Iterator):
    def __init__(self, stream, cset=None, sort=True):
        self.stream = stream
        self.labels = cset.tolist() if cset else None
        self.sort = sort

    def next(self):
        values = []
        while True:
            line = self.stream.next().strip()
            if not line:
                break
            values.append(self.__parse_line(line))
        labels = self.labels if self.labels else range(len(values))
        preds = zip(labels, softmax(values))
        if self.sort:
            preds.sort(key=lambda x: x[1], reverse=True)
        return preds

    def __parse_line(self, line):
        return float(line.rstrip().rsplit(":", 1)[-1])


