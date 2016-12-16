import os
import sys
import shutil
import cPickle as pickle

sys.path.insert(0, os.path.dirname(__file__))

from vwgec.settings import config
from utils import cmd
from logger import log


class FeatureFilter(object):
    def __init__(self, freq_file, min_freq=None, limit=2000000, create_from=None):
        self.freq_file = freq_file
        min_freq = min_freq or config['feature-freq'] or 5
        self.feats = set()

        if create_from:
            self.__calculate_freqs(create_from, freq_file + '.txt')
            self.__binarize_freqs(freq_file + '.txt', freq_file, min_freq, limit)
        if os.path.exists(freq_file):
            self.__load_feats(freq_file)

    def __load_feats(self, freq_file):
        log.info("Load features from {}".format(freq_file))
        with open(freq_file) as freq_io:
            self.feats = pickle.load(freq_io)
        log.info("Load {} features".format(len(self.feats)))

    def __calculate_freqs(self, feat_file, freq_file):
        command = r"cat {feats}" \
                " | grep '^shared' | cut -c11-" \
                " | tr ' ' '\\n' | sort -S 5G --parallel {threads}" \
                " | uniq -c | sort -rn -S 5G --parallel {threads}" \
                " | sed -r 's/ +([0-9]+)/\\1\\t/'" \
                " > {freqs}"
        cmd.run(
            command.format(
                feats=feat_file, freqs=freq_file, threads=config['threads']))

    def __binarize_freqs(self, freq_txt, freq_bin, min_freq, limit):
        log.info("Binarize features {}, min.freq= {} limit= {}" \
                .format(freq_txt, min_freq, limit))
        feats = []
        with open(freq_txt) as freq_io:
            for i, line in enumerate(freq_io):
                count, feat = line.strip().split()
                if int(count) < min_freq or i > limit:
                    break
                feats.append(feat)

        log.info("Binarize {} features".format(len(feats)))
        with open(freq_bin, 'wb') as bin_io:
            pickle.dump(set(feats), bin_io)


    def filter(self, feat_file):
        if not self.feats:
            log.error("Feature frequencies not calculated!")

        shutil.move(feat_file, feat_file + '.all')
        feat_out = open(feat_file, 'w+')

        n_before = 0
        n_after = 0

        with open(feat_file + '.all') as feat_in:
            for line in feat_in:
                if line.startswith("shared"):
                    all_feats = line.rstrip()[10:].split()
                    n_before += len(all_feats)

                    new_feats = [f for f in all_feats if f in self.feats]
                    n_after += len(new_feats)

                    feat_out.write("shared |s {}\n".format(' '.join(new_feats)))
                else:
                    feat_out.write(line)

        log.info("Number of source features before filtering: {}".format(n_before))
        log.info("Number of source features after filtering: {}".format(n_after))
        feat_out.close()
