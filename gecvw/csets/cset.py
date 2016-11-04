import os
import sys
import re

sys.path.insert(0, os.path.dirname(__file__))

from logger import log


class CWord:
    NULL = '<null>'
    COMMA = '<comma>'


class CSet:
    SPECIAL_CWORDS = {'': CWord.NULL, ',': CWord.COMMA}

    def __init__(self, cset, sep=','):
        self.cset = self.__parse_cset(cset, sep)
        self.labels = {self.cword_to_label(cw): cw for cw in self.cset}
        log.debug("initialize {}".format(self))

        self.patterns = {r'^' + cw.replace('*', r'\w{3,}') + r'$': cw
                         for cw in self.cset if '*' in cw}
        self.regex = '|'.join(r'^' + cw.replace('*', r'\w{3,}') + r'$'
                              for cw in self.cset).replace(CWord.NULL, '')

    def include(self, word):
        cw = CSet.SPECIAL_CWORDS.get(word, word).lower()
        return re.match(self.regex, cw)

    def match(self, word):
        cw = CSet.SPECIAL_CWORDS.get(word, word).lower()
        if cw in self.cset:
            return cw
        for pattern in self.patterns:
            if re.match(pattern, cw):
                return self.patterns[pattern]
        return None

    def has_null(self):
        return CWord.NULL in self.cset

    def size(self):
        return len(self.cset)

    def cword_to_label(self, word, start_from=0):
        return self.cset.index(word) + start_from

    def label_to_cword(self, label, start_from=0):
        num_label = int(label)
        if num_label - start_from < len(self.cset) and num_label >= 0:
            return self.cset[num_label - start_from]
        return None

    def __parse_cset(self, words, separator):
        cset = [CSet.SPECIAL_CWORDS.get(w, w).lower()
                for w in words.split(separator)]
        return sorted(list(set(cset)))

    def __build_regex_cs(self, cset):
        return {cw: cw.replace('*', r'\w{3,}') for cw in cset if '*' in cw}

    def __iter__(self):
        for cw in self.cset:
            yield cw

    def __str__(self):
        return "%s" % self.labels

    def __repr__(self):
        return """<ConfusionSet %s>""" % self.cset
