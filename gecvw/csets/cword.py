import os
import sys

sys.path.insert(0, os.path.dirname(__file__))


class CWord:
    NULL = '<null>'
    COMMA = '<comma>'
    UNK = '<unk>'

    def __init__(self, i, j, err_tok, cor_tok, src_cw, tgt_cw):
        self.pos = (i, j)
        self.err = err_tok
        self.cor = cor_tok
        self.src = src_cw
        self.tgt = tgt_cw

    def __iter__(self):
        for field in [self.pos[0], self.pos[1], self.err, self.cor, self.src,
                      self.tgt]:
            yield field

    def __str__(self):
        return "({},{}) [{},{}] {} => {}".format(
            self.pos[0], self.pos[1], self.src, self.tgt, self.err, self.cor)

    def __repr__(self):
        return "CWord({},{} {},{})".format(
            self.pos[0], self.pos[1], self.src, self.tgt)

    @staticmethod
    def is_null(word):
        return word != '' and word != '<null>'
