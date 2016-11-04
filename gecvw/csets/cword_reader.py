import os
import sys

sys.path.insert(0, os.path.dirname(__file__))


class CWordReader(object):
    """
    Reads and formats .cword files in the form of:
    <sid>\t<start_pos>\t<end_pos>\t<src_word>\t<trg_word>\t<src_cword>\t<trg_cword>
    """

    NUM_FIELDS = 7

    def read_line(self, line):
        fields = line.strip().split("\t")
        if len(fields) != CWordReader.NUM_FIELDS:
            raise Exception("Incorrectly formatted line: {}".format(line.strip()))
        return tuple([int(v) for v in fields[:3]] + fields[3:])

    def format_line(self, sid, fields):
        if len(fields) != CWordReader.NUM_FIELDS - 1:
            raise Exception("Incorrect number of fields: {}".format(fields))
        return "\t".join(str(v) for v in [sid] + list(fields))
