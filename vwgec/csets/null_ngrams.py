import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from vwgec.settings import config
from csets.cset import CSet
from csets.cword import CWord
from utils import cmd

from logger import log

DEBUG_COUNTER = 50000


class NullNGrams(object):
    def __init__(self, file_name, min_count=0, limit=None):
        self.file_name = file_name
        self.factor = None
        self.lc = None
        self.rc = None
        self.min_count = 0
        self.limit = limit

        self.ngrams = set()
        self.__load_ngrams(file_name)

    def __contains__(self, key):
        return key in self.ngrams

    def __load_ngrams(self, file_name):
        ngrams = []
        with open(file_name) as f:
            for i, line in enumerate(f):
                if i == 0:
                    self.factor, lc, rc = line.strip().split()
                    self.lc = int(lc)
                    self.rc = int(rc)
                    log.info("Load ngrams {} (factor={} contexts={},{})".format(
                        file_name, self.factor, self.lc, self.rc))
                    continue
                ngram, count = line.strip().split("\t")
                if self.limit and i > self.limit:
                    break
                if count < self.min_count:
                    break
                ngrams.append(ngram)
            log.info("Loaded {} ngrams".format(len(ngrams)))
            self.ngrams = set(ngrams)

    @staticmethod
    def init(file_name, factor, left_context, right_context):
        with open(file_name, 'w+') as f:
            f.write("{} {} {}\n".format(factor, left_context, right_context))

    @staticmethod
    def load(file_name, min_count=None, limit=None):
        with open(file_name, 'r') as f:
            factor, lc, rc = f.next().strip().split()
        return NullNGrams(file_name, min_count, limit)


class NullNGramsFinder(object):
    def __init__(self, left_context=2, right_context=2, min_count=5):
        self.cset = CSet(config['source-cset'])
        self.lc = left_context
        self.rc = right_context
        self.min_count = min_count
        self.clean = False

    def find_ngrams(self, corpus, input_file, ngram_file=None, factor='tok'):
        """
        Extracts n-grams for a factor given as input file.
        """
        list_file = self.__extract_ngram_list(corpus, input_file)
        freq_file = self.__count_frequencies(list_file)

        if ngram_file is None:
            ngram_file = input_file + '.nulls'
        ngrams = NullNGrams.init(ngram_file, factor, self.lc, self.rc)
        self.__save_ngrams(freq_file, ngram_file)

        if self.clean:
            log.debug("Remove temporary files")
            os.remove(list_file)
            os.remove(freq_file)

        return ngram_file

    def __extract_ngram_list(self, corpus, input_file):
        input_io = open(input_file)
        list_io = open(input_file + '.nulls.list', 'w+')

        with open(corpus) as corpus_io:
            for i, line in enumerate(corpus_io):
                words = line.strip().split()

                tokens = input_io.next().strip().lower().split()
                ngrams = self.__extract_ngrams(words, tokens)
                if ngrams:
                    list_io.write("\n".join(ngrams) + "\n")

                if 0 == (i + 1) % DEBUG_COUNTER:
                    log.debug("[{}]".format(i + 1))

        input_io.close()
        list_io.close()

        return input_file + '.nulls.list'

    def __count_frequencies(self, list_file):
        log.info("Calculate n-gram frequencies in file {}...".format(
            list_file))
        command = "cat {0}" \
                " | sort -S 10G --parallel 8" \
                " | uniq -c" \
                " | sort -S 10G --parallel 8 -nr" \
                " > {0}.freq".format(list_file)
        cmd.run(command)

        return list_file + '.freq'

    def __save_ngrams(self, freq_file, ngram_file):
        log.debug("Write n-gram frequencies into file {}...".format(
            ngram_file))
        line_num = cmd.run("cat {0} | grep -Pn '^ +{1} .*' | tr ':' '\\t'" \
            " | cut -f1 | tail -1".format(freq_file, self.min_count))
        cmd.run("head -n {} {} | sed -r 's/^ *([0-9]+) (.*)/\\2\\t\\1/' >> {}" \
            .format(line_num.strip(), freq_file, ngram_file))

    def __extract_ngrams(self, tokens, tags):
        tags = self.__add_sentence_marks(tags)
        ngrams = []
        for i, word in enumerate(tokens):
            j = i + self.lc
            # TODO: check if this is still OK
            if self.cset.include(word):
                ngram = self.__ngram(j, tags)
                if ngram is not None:
                    ngrams.append(ngram)
        return ngrams

    def __add_sentence_marks(self, tokens):
        return ['<s>'] * self.lc + tokens + ['</s>'] * self.rc

    def __ngram(self, i, tokens, length=1):
        grams = tokens[i - self.lc:i] + tokens[i + length:i + length + self.rc]
        if len(grams) != (self.lc + self.rc):
            return None
        return ' '.join(grams)
