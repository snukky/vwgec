import os
import sys
import math

from collections import Iterator

sys.path.insert(0, os.path.dirname(__file__))

from csets.cword_reader import CWordReader
from logger import log


class LDFIterator(Iterator):
    def __init__(self, stream, cset):
        self.stream = stream
        self.cset = cset

    def next(self):
        values = []
        for i in xrange(len(self.cset)):
            value = float(self.stream.next().strip().split(":", 1)[-1])
            values.append(value)
        # skip empty line
        self.stream.next()

        preds = zip(self.cset.cset, self.__softmax(values))
        preds.sort(key=lambda x: x[1], reverse=True)
        return preds

    def __softmax(self, xs):
        norm = sum(math.exp(x) for x in xs)
        return [math.exp(x) / norm for x in xs]

class Prediction(object):
    def __iter__(self, preds):
        self.preds = {}


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
