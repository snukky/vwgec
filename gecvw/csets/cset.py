import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from logger import log


class CWord:
    NULL = '<null>'
    COMMA = '<comma>'


class CSet:
    SPECIAL_CWORDS = {'': CWord.NULL, ',': CWord.COMMA}

    def __init__(self, cset):
        self.cs = self.__parse_cset(cset)
        self.labels = {self.word_to_label(word): word for word in self.cs}
        log.debug("initialize " + self.__str__())

    def include(self, word):
        cw = CSet.SPECIAL_CWORDS.get(word, word).lower()
        return cw in self.cs

    def match(self, word):
        cw = CSet.SPECIAL_CWORDS.get(word, word).lower()
        if cw in self.cs:
            return cw
        return None

    def has_null(self):
        return CWord.NULL in self.cs

    def size(self):
        """Returns number of confused words."""
        return len(self.cs)

    def word_to_label(self, word, start_from=0):
        if self.include(word):
            cw = CSet.SPECIAL_CWORDS.get(word, word)
            return self.cs.index(cw.lower()) + start_from
        return None

    def label_to_word(self, label, start_from=0):
        num_label = int(label)
        if num_label - start_from < len(self.cs) and num_label >= 0:
            return self.cs[num_label - start_from]
        return None

    def __parse_cset(self, words):
        cs = [CSet.SPECIAL_CWORDS.get(w, w).lower() for w in words.split(',')]
        cs = [',' if w == '<comma>' else w for w in cs]
        return sorted(list(set(cs)))

    def __iter__(self):
        for cw in self.cs:
            yield cw

    def __str__(self):
        return "%s" % self.labels

    def __repr__(self):
        return """<ConfusionSet %s>""" % self.cs
