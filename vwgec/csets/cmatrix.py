import os
import sys

from collections import Counter
from collections import defaultdict
from operator import itemgetter

import cPickle as pickle

sys.path.insert(0, os.path.dirname(__file__))

from csets.cword_reader import CWordReader
from csets.cword import CWord
from logger import log


class CMatrixBuilder(object):
    def __init__(self):
        self.matrix = defaultdict(dict)

    def build(self, cword_io, min_a_count, min_b_count):
        ab_counts = Counter()
        aa_counts = Counter()
        ab_edits = {}
        reader = CWordReader(cword_io)

        log.info("Extracting (a,b) edits")
        for sid, (_, _, _, _, a, b) in reader:
            if a == b:
                continue
            if a not in ab_edits:
                ab_edits[a] = Counter()
            ab_edits[a][b] += 1
            ab_counts[a] += 1

        log.info("Building matrix with counts")
        n = 0
        for a in sorted(ab_counts, key=ab_counts.__getitem__, reverse=True):
            if ab_counts[a] < min_a_count:
                break

            bs = {b: count
                  for b, count in ab_edits[a].iteritems()
                  if count >= min_b_count}

            if len(bs):
                self.matrix[a] = bs

                # determine which AA counts will be needed to collect
                aa_counts[a] = 0
                for b in bs:
                    aa_counts[b] = 0
            n += len(bs)

        del ab_edits

        log.info("Counting (a,a) edits")
        reader.rewind()
        for sid, (_, _, _, _, a, b) in reader:
            if a == b and a in aa_counts:
                aa_counts[a] += 1
                self.matrix[a][a] = 0
                n += 1

        del ab_counts

        log.info("Calculating probabilities")
        for a in aa_counts:
            for b in self.matrix[a]:
                ab_count = self.matrix[a][b]
                ab_prob = ab_count / float(n)
                self.matrix[a][b] = (ab_count, ab_prob)
            aa_count = aa_counts[a]
            aa_prob = aa_count / float(n)
            self.matrix[a][a] = (aa_count, aa_prob)

        return CMatrix(self.matrix)


class CMatrix(object):
    def __init__(self, matrix):
        self.matrix = matrix
        self.n = sum(sum(c for c, _ in bs.values()) for bs in self.matrix.values())
        self.__calculate_statistics()

    @staticmethod
    def load(file_name):
        with open(file_name, 'rb') as file_io:
            matrix = pickle.load(file_io)
            return CMatrix(matrix, counts)

    def save(self, file_name):
        with open(file_name, 'wb') as file_io:
            pickle.dump(self.matrix, file_io)

    def sorted_edits(self):
        edits = [(a, b, count, prob)
                 for a, words in self.matrix.iteritems()
                 for b, (count, prob) in words.iteritems()]
        return sorted(edits, key=itemgetter(0, 2), reverse=True)

    def stats(self):
        return {
            'aa_count': self.aa_count / float(self.n),
            'ab_count': self.ab_count / float(self.n),
            'sub': self.num_sub / float(self.ab_count),
            'del': self.num_del / float(self.ab_count),
            'ins': self.num_ins / float(self.ab_count)
        }

    def __calculate_statistics(self):
        self.aa_count = 0
        self.ab_count = 0
        self.num_sub = 0
        self.num_del = 0
        self.num_ins = 0

        for a, bs in self.matrix.iteritems():
            for b, (c,f) in bs.iteritems():
                if a == b:
                    self.aa_count += c
                else:
                    self.ab_count += c

                if a != CWord.NULL and b == CWord.NULL:
                    self.num_del += c
                elif a == CWord.NULL and b != CWord.NULL:
                    self.num_ins += c
                elif a != b:
                    self.num_sub += c
