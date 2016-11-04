import os
import sys

from difflib import SequenceMatcher

sys.path.insert(0, os.path.dirname(__file__))

from csets.cset import CSet, CWord
from logger import log


class CWordFinder():
    def __init__(self, src_cset, trg_cset, train=False):
        self.train = train
        self.src_cset = src_cset
        self.trg_cset = trg_cset
        self.count = 0

    def find_confusion_words(self, line):
        err_toks, edits = self.parse_corpus_line(line)
        added = False

        for i, err in enumerate(err_toks):
            if (i, i + 1) in edits:
                cor, err_cw, cor_cw = edits[(i, i + 1)][1:]
                if self.trg_cset.include(cor):
                    yield (i, i + 1, err, cor, err_cw, cor_cw)
                    self.count += 1
                    added = True
            elif (i, i) in edits and self.train and self.src_cset.has_null():
                err, cor, err_cw, cor_cw = edits[(i, i)]
                yield (i, i, err, cor, err_cw, cor_cw)
                self.count += 1
                added = False
            else:
                err_cw = self.src_cset.match(err)
                if err_cw is None:
                    continue
                yield (i, i + 1, err, err, err_cw, err_cw)
                self.count += 1
                added = True
                added = False

    def parse_corpus_line(self, line):
        if "\t" in line:
            err_toks, cor_toks = [sent.split()
                                  for sent in line.strip().split("\t")]
            edits = self.find_edits(err_toks, cor_toks)
        else:
            err_toks = line.strip().split()
            edits = {}
        return (err_toks, edits)

    def find_edits(self, err_toks, cor_toks):
        matcher = SequenceMatcher(None, err_toks, cor_toks)
        edits = {}

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            err_tok = ' '.join(err_toks[i1:i2])
            cor_tok = ' '.join(cor_toks[j1:j2])

            if tag == 'replace':
                err_cw = self.src_cset.match(err_tok)
                if err_cw is None:
                    continue
                cor_cw = self.trg_cset.match(cor_tok)
                if cor_cw is None:
                    continue
                if not self.__check_if_cwords_are_compatible(err_tok, cor_tok,
                                                             err_cw, cor_cw):
                    continue
                edits[(i1, i2)] = (err_tok, cor_tok, err_cw, cor_cw)
            elif tag == 'insert':
                cor_cw = self.trg_cset.match(cor_tok)
                if cor_cw:
                    edits[(i1, i2)] = ('', cor_tok, CWord.NULL, cor_cw)
            elif tag == 'delete':
                err_cw = self.src_cset.match(err_tok)
                if err_cw:
                    edits[(i1, i2)] = (err_tok, '', err_cw, CWord.NULL)
        return edits

    def __check_if_cwords_are_compatible(self, w1, w2, cw1, cw2):
        """
        Two confusion words are compatible if stars in their patterns covers
        the same substrings.
        """
        if '*' not in cw1 or '*' not in cw2:
            return True
        i1 = cw1.find('*')
        j1 = len(cw1) - i1 - 1
        i2 = cw2.find('*')
        j2 = len(cw2) - i2 - 1
        return w1[i1:-j1] == w2[i2:-j2]
