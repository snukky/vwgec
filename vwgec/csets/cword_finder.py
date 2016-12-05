import os
import sys

from difflib import SequenceMatcher

sys.path.insert(0, os.path.dirname(__file__))

from csets.cword import CWord
from csets.cset import CSetPair
from logger import log


class CWordFinder():
    def __init__(self, cset_pair, train=False, extra_finders=[]):
        self.train = train
        self.csets = cset_pair
        self.count = 0
        self.extra_finders = extra_finders

    def find_confusion_words(self, line, fact_toks=None):
        err_toks, edits = self.__parse_corpus_line(line)

        for finder in self.extra_finders:
            edits = finder.update_edits(edits, err_toks, fact_toks)
        added = False

        # log.warn("Edits: {}".format(edits))

        for i, err in enumerate(err_toks):
            if (i, i + 1) in edits:
                cor, src_cw, tgt_cw, _ = edits[(i, i + 1)][1:]
                # log.warn('1: {} {} {} {}'.format(err, cor, src_cw, tgt_cw))
                if self.csets.tgt.include(cor):
                    yield CWord(i, i + 1, err, cor, src_cw, tgt_cw)
                    self.count += 1
                    added = True

            elif (i, i) in edits:
                err, cor, src_cw, tgt_cw, train_only = edits[(i, i)]
                if not self.csets.src.has_null():
                    continue
                if train_only and not self.train:
                    continue
                # log.warn('2: {} {} {} {}'.format(err, cor, src_cw, tgt_cw))
                yield CWord(i, i, err, cor, src_cw, tgt_cw)
                self.count += 1
                added = False

            else:
                src_cw = self.csets.src.match(err)
                # log.warn('3: {} {}'.format(err, src_cw))
                if src_cw is None or src_cw == '*':
                    continue
                yield CWord(i, i + 1, err, err, src_cw, src_cw)
                self.count += 1
                added = True
                added = False

    def __parse_corpus_line(self, line):
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
                edits[(i1, i2)] = (err_tok, cor_tok, src_cw, tgt_cw, False)
            elif tag == 'insert':
                tgt_cw = self.csets.tgt.match(cor_tok)
                if tgt_cw:
                    edits[(i1, i2)] = ('', cor_tok, CWord.NULL, tgt_cw, True)
            elif tag == 'delete':
                src_cw = self.csets.src.match(err_tok)
                if src_cw:
                    edits[(i1, i2)] = (err_tok, '', src_cw, CWord.NULL, False)
        return edits

    def add_extra_finder(self, finder):
        self.extra_finders.append(finder)
