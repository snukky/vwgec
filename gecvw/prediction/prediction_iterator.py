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
    def __init__(self, txt_file, cword_file, pred_file, cset):
        self.txt_file = txt_file
        self.cword_file = cword_file
        self.pred_file = pred_file
        self.cset = cset

    def __iter__(self):
        pred_io = open(self.pred_file)
        txt_io = open(self.txt_file)
        cword_reader = CWordReader(self.cword_file)
        preds_iter = LDFIterator(pred_io, self.cset)

        sid, cword = cword_reader.next()
        preds = preds_iter.next()

        n = 0
        for line in txt_io:
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

        txt_io.close()
        pred_io.close()
