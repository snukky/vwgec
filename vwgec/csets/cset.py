import os
import sys
import re

sys.path.insert(0, os.path.dirname(__file__))

from csets.cword import CWord
from logger import log


class CSetPair:
    def __init__(self, src_cset, tgt_cset, sep=','):
        self.src = CSet(src_cset, sep)
        self.tgt = CSet(tgt_cset, sep)

    def are_compatible(self, w1, w2, cw1, cw2):
        """
        Two confusion words are compatible if stars in their patterns covers
        the same substrings.
        """
        if '*' == cw1 == cw2:
            return False
        if '*' not in cw1 or '*' not in cw2:
            return True
        i1 = cw1.find('*')
        j1 = len(w1) if cw1 == '*' else (len(cw1) - i1 - 1) * -1
        i2 = cw2.find('*')
        j2 = len(w2) if cw2 == '*' else (len(cw2) - i2 - 1) * -1
        return w1[i1:j1] == w2[i2:j2]

    @staticmethod
    def construct_correction(w1, cw1, cw2):
        # TODO: Handle the case when w1 is <null>
        if '*' not in cw2:
            return '' if cw2 == "<null>" else cw2
        i1 = cw1.find('*')
        j1 = len(cw1) - i1 - 1
        return cw2.replace('*', w1[i1:-j1])

    def construct_target_word(self, w1, cw1, cw2):
        return CSetPair.construct_correction(w1, cw1, cw2)


class CSet:
    SPECIAL_CWORDS = {'': CWord.NULL, ',': CWord.COMMA}

    def __init__(self, cset, sep=','):
        self.cset = self.__parse_cset(cset, sep)
        self.labels = dict(enumerate(self.cset))
        log.info("Initialize {}".format(self))

        self.regex = self.__init_regex()
        self.patterns = {r'^' + cw.replace('*', r'\w{3,}') + r'$': cw
                         for cw in self.cset if '*' in cw}

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

    def tolist(self):
        return self.cset

    def cword_to_label(self, word, start_from=0):
        return self.cset.index(word) + start_from

    def label_to_cword(self, label, start_from=0):
        num_label = int(label)
        if num_label - start_from < len(self.cset) and num_label >= 0:
            return self.cset[num_label - start_from]
        return None

    def __parse_cset(self, words, separator=','):
        cset = [CSet.SPECIAL_CWORDS.get(w, w).lower()
                for w in words.split(separator)]
        return sorted(list(set(cset)))

    def __init_regex(self):
        regex = '|'.join(r'^' + cw.replace('*', r'\w{3,}') + r'$'
                         for cw in self.cset)

        for w, cw in CSet.SPECIAL_CWORDS.iteritems():
            if cw in self.cset:
                regex += '|^{}$'.format(w)
        return regex

    def __iter__(self):
        for cw in self.cset:
            yield cw

    def __len__(self):
        return len(self.cset)

    def __str__(self):
        return "%s" % self.labels

    def __repr__(self):
        return """<ConfusionSet %s>""" % self.cset
