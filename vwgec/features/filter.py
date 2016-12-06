import os
import sys
import shutil

sys.path.insert(0, os.path.dirname(__file__))

from vwgec.settings import config
from utils import cmd
from logger import log


class FeatureFilter(object):
    def __init__(self, freq_file, min_freq=None, limit=2000000, create_from=None):
        self.freq_file = freq_file
        self.min_freq = min_freq or config['feature-freq'] or 5
        self.feats = set()

        if create_from:
            self.__calculate_freqs(create_from, freq_file)
        if os.path.exists(self.freq_file):
            self.__load_feats(self.min_freq, limit)

    def __load_feats(self, min_freq, limit):
        log.info("Load features {}, min.freq= {} limit= {}" \
                .format(self.freq_file, min_freq, limit))
        feats = []
        with open(self.freq_file) as freq_io:
            for i, line in enumerate(freq_io):
                count, feat = line.strip().split()
                if int(count) < min_freq or i > limit:
                    break
                feats.append(feat)
        log.info("{} features loaded".format(len(feats)))
        self.feats = set(feats)

    def __calculate_freqs(self, feat_file, freq_file):
        command = r"cat {}" \
                " | grep '^shared' | cut -c11-" \
                " | tr ' ' '\\n' | sort | uniq -c | sort -rn" \
                " | sed -r 's/ +([0-9]+)/\\1\\t/'" \
                " > {}"
        cmd.run(command.format(feat_file, freq_file))

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
