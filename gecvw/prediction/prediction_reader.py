import os
import sys
import math

from collections import Iterator

sys.path.insert(0, os.path.dirname(__file__))

from csets.cset import CSet
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


class PredictionReader(object):
    def __init__(self, txt_io, cword_io, pred_io, cset, open_files=False):
        self.txt_io = txt_io
        self.cword_io = cword_io
        self.pred_io = pred_io
        self.cset = CSet(cset) if cset is not None else None
        self.open_files = open_files

    def __iter__(self):
        if self.open_files:
            self.txt_io = open(self.txt_io)
            self.cword_io = open(self.cword_io)
            self.pred_io = open(self.pred_io)
        else:
            self.txt_io.seek(0)
            self.cword_io.seek(0)
            self.pred_io.seek(0)

        cword_reader = CWordReader(self.cword_io)
        preds_iter = LDFIterator(self.pred_io, self.cset)

        sid, cword = cword_reader.next()
        preds = preds_iter.next()

        n = 0
        for line in self.txt_io:
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

        if self.open_files:
            self.txt_io.close()
            self.txt_io = self.txt_io.name
            self.cword_io.close()
            self.cword_io = self.cword_io.name
            self.pred_io.close()
            self.pred_io = self.pred_io.name
