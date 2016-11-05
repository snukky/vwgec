import os
import sys

from difflib import SequenceMatcher

sys.path.insert(0, os.path.dirname(__file__))

from csets.cword import CWord
from csets.cset import CSetPair
from logger import log


class CWordFinder():
    def __init__(self, cset_pair, train=False):
        self.train = train
        self.csets = cset_pair
        self.count = 0

    def find_confusion_words(self, line):
        err_toks, edits = self.parse_corpus_line(line)
        added = False

        for i, err in enumerate(err_toks):
            if (i, i + 1) in edits:
                cor, src_cw, tgt_cw = edits[(i, i + 1)][1:]
                if self.csets.tgt.include(cor):
                    yield CWord(i, i + 1, err, cor, src_cw, tgt_cw)
                    self.count += 1
                    added = True
            elif (i, i) in edits and self.train and self.csets.src.has_null():
                err, cor, src_cw, tgt_cw = edits[(i, i)]
                yield CWord(i, i, err, cor, src_cw, tgt_cw)
                self.count += 1
                added = False
            else:
                src_cw = self.csets.src.match(err)
                if src_cw is None:
                    continue
                yield CWord(i, i + 1, err, err, src_cw, src_cw)
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
                src_cw = self.csets.src.match(err_tok)
                if src_cw is None:
                    continue
                tgt_cw = self.csets.tgt.match(cor_tok)
                if tgt_cw is None:
                    continue
                if not self.csets.are_compatible(err_tok, cor_tok, src_cw,
                                                tgt_cw):
                    continue
                edits[(i1, i2)] = (err_tok, cor_tok, src_cw, tgt_cw)
            elif tag == 'insert':
                tgt_cw = self.csets.tgt.match(cor_tok)
                if tgt_cw:
                    edits[(i1, i2)] = ('', cor_tok, CWord.NULL, tgt_cw)
            elif tag == 'delete':
                src_cw = self.csets.src.match(err_tok)
                if src_cw:
                    edits[(i1, i2)] = (err_tok, '', src_cw, CWord.NULL)
        return edits
