import os
import sys
import codecs
import difflib
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from vwgec.settings import config
from vwgec.settings import SCRIPTS_DIR
from utils import cmd
from logger import log

QUOTES = ('"', '``', "''")


def convert_tok(file_in, file_out, mode='moses-nltk'):
    if not mode:
        converter = ''
    elif mode == 'moses-nltk':
        converter = \
            ' | {moses}/scripts/tokenizer/detokenizer.perl -l en' \
            ' | python {scripts}/nltk-tok.py' \
            .format(moses=config['mosesdecoder'], scripts=SCRIPTS_DIR)
    elif mode == 'nltk-moses':
        converter = \
            ' | python {scripts}/nltk-detok.py' \
            ' | {moses}/scripts/tokenizer/tokenizer.perl -l en -threads {threads}' \
            .format(moses=config['mosesdecoder'], scripts=SCRIPTS_DIR,
                    threads=config['threads'])
    else:
        log.error("Convertion mode '{}' not supported".format(mode))
        exit(1)
    cmd.run("cat {} {} > {}".format(file_in, converter, file_out))


def restore_tok(file_in, file_orig, file_out, quotes=True):
    out_io = open(file_out, 'w+')
    with open(file_in) as file_io, open(file_orig) as orig_io:
        for line in file_io:
            sent = line.strip()
            sent_orig = orig_io.next().strip()
            sent_new = restore_sentence_tok(sent, sent_orig, quotes)
            out_io.write(sent_new + "\n")
    out_io.close()


def restore_sentence_tok(sent, orig_sent, quotes=False, debug=False):
    if debug:
        log.debug(u'toks: {}'.format(sent).encode('utf8', 'replace'))
        log.debug(u'orig: {}'.format(orig_sent).encode('utf8', 'replace'))

    toks = sent.split()
    orig_toks = orig_sent.split()

    matcher = difflib.SequenceMatcher(None, toks, orig_toks)
    new_toks = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal' and debug:
            log.debug(u"  {}: ({},{}) '{}' -> ({},{}) '{}'" \
                .format(tag,
                        i1, i2, ' '.join(toks[i1:i2]),
                        j1, j2, ' '.join(orig_toks[j1:j2])) \
                .encode('utf8', 'replace'))

        if tag == 'equal':
            new_toks += orig_toks[j1:j2]

        elif tag == 'replace':
            ctok = ''.join(toks[i1:i2])
            orig_ctok = ''.join(orig_toks[j1:j2])

            if quotes:
                if ctok in QUOTES and orig_ctok in QUOTES:
                    new_toks += orig_toks[j1:j2]
                    continue
                elif toks[i1:i2][0] in QUOTES and orig_toks[j1:j2][
                        0] in QUOTES:
                    toks[i1] = orig_toks[j1]
                elif i2 - i1 > 1 and toks[i1:i2][1] in QUOTES and orig_toks[
                        j1:j2][0] in QUOTES:
                    toks[i1 + 1] = orig_toks[j1]
                elif j2 - j1 > 1 and toks[i1:i2][0] in QUOTES and orig_toks[
                        j1:j2][1] in QUOTES:
                    toks[i1] = orig_toks[j1 + 1]
                elif i2 - i1 > 1 and j2 - j1 > 1 and toks[i1:i2][
                        1] in QUOTES and orig_toks[j1:j2][1] in QUOTES:
                    toks[i1 + 1] = orig_toks[j1 + 1]

            if ctok == orig_ctok:
                new_toks += orig_toks[j1:j2]
            else:
                new_toks += toks[i1:i2]

        elif tag == 'delete':
            new_toks += toks[i1:i2]

        elif tag == 'insert':
            pass

    new_sent = ' '.join(new_toks)
    if debug:
        log.debug('    : {}'.format(new_sent.encode('utf8', 'replace')))
    return new_sent
