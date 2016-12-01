import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from csets.cword import CWord


class CWordReader(object):
    """
    Reads and formats .cword files in the form of:
    <sid>\t<start_pos>\t<end_pos>\t<src_word>\t<trg_word>\t<src_cword>\t<trg_cword>
    """

    NUM_FIELDS = 7

    def __init__(self, stream):
        self.stream = stream

    def __iter__(self):
        for line in self.stream:
            yield CWordReader.read_line(line)

    def next(self):
        return CWordReader.read_line(self.stream.next())

    def format(self, sid, cword):
        self.stream.write(CWordReader.format_line(sid, cword) + "\n")

    def rewind(self):
        self.stream.seek(0)

    @staticmethod
    def read_line(line):
        fields = line.strip().split("\t")
        if len(fields) != CWordReader.NUM_FIELDS:
            raise Exception("Incorrectly formatted line: {}".format(line))
        return int(fields[0]), CWord(
            int(fields[1]), int(fields[2]), *fields[3:])

    @staticmethod
    def format_line(sid, cword):
        return "\t".join(str(v) for v in [sid] + list(cword))
