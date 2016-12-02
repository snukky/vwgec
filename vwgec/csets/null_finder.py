import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from vwgec.settings import config
from csets.cword import CWord
from csets.null_ngrams import NullNGrams
from factors import FACTORS

from logger import log


class NullFinder(object):
    def __init__(self, cset, ngram_file, min_count=1):
        self.cset = cset
        self.ngrams = NullNGrams.load(ngram_file, min_count, limit=5000)
        self.lc = self.ngrams.lc
        self.rc = self.ngrams.rc

    def update_edits(self, edits, err_toks, fact_toks):
        factor_id = FACTORS.TAGS[self.ngrams.factor]

        err_tags = fact_toks[factor_id]
        if err_tags is None:
            log.warn("Missing required '{}' tags!".format(self.ngrams.factor))
            return edits
        new_edits = self.find_nulls(err_toks, err_tags, edits)

        n = len(new_edits) - len(edits)
        if n > 0:
            log.info("Found {} more edits".format(n))

        return new_edits

    def find_nulls(self, tokens, tags, edits):
        skip = False
        tags_with_marks = self.__add_sentence_marks(tags)

        for i, err in enumerate(tokens):
            if skip:
                skip = False
                continue

            # TODO: make single if statement
            if (i, i + 1) in edits:
                continue
                skip = True

            elif self.cset.include(err):
                continue
                skip = True

            else:
                j = i + self.lc
                ngram = self.__ngram(j, tags_with_marks)
                if ngram is not None and ngram in self.ngrams:
                    if (i, i) not in edits:
                        edits[(i, i)] = ('', '', CWord.NULL, CWord.NULL)
        return edits

    def __add_sentence_marks(self, tokens):
        return ['<s>'] * self.lc + tokens + ['</s>'] * self.rc

    def __ngram(self, i, tokens):
        grams = tokens[i - self.lc:i] + tokens[i:i + self.rc]
        if len(grams) != (self.lc + self.rc):
            return None
        return ' '.join(grams)
