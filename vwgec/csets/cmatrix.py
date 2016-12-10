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

    def build(self, cword_io):
        aa_counts = Counter()
        reader = CWordReader(cword_io)
        n = 0

        log.info("Count edits")
        for sid, (_, _, _, _, a, b) in reader:
            if a not in self.matrix:
                self.matrix[a] = defaultdict(int)
            self.matrix[a][b] += 1
            if a == b:
                aa_counts[a] += 1
            n += 1

        log.info("Calculate probabilities")
        for a in aa_counts:
            for b in aa_counts:
                if b in self.matrix[a]:
                    count = self.matrix[a][b]
                    prob = count / float(n)
                    self.matrix[a][b] = (count, prob)
                else:
                    self.matrix[a][b] = (0, 0.0)

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
        log.info("Edits n={} AA={} AB={}" \
            .format(self.n, self.aa_count, self.ab_count))
        log.info("Operations SUB={} DEL={} INS={}" \
            .format( self.num_sub, self.num_del, self.num_ins))
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
                else:
                    log.warn("{} {}".format(a, b))
