import os
import sys
import math

from collections import Iterator

sys.path.insert(0, os.path.dirname(__file__))

from csets.cword_reader import CWordReader
from utils.softmax import softmax
from logger import log


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


class PredictionIterator(object):
    def __init__(self, text, cwords, preds, cset):
        self.text = text
        self.cwords = open(cwords)
        self.preds = open(preds)
        self.cset = cset

    def __iter__(self):
        cword_reader = CWordReader(self.cwords)
        preds_iter = LDFIterator(self.preds, self.cset)

        sid, cword = cword_reader.next()
        preds = preds_iter.next()

        n = 0
        for line in self.text:
            data = []
            while sid == n:
                data.append((cword, preds))
                try:
                    sid, cword = cword_reader.next()
                    preds = preds_iter.next()
                except StopIteration:
                    break
            yield (n, line.split("\t", 1)[0], data)
            n += 1

        self.cwords.close()
        self.preds.close()
