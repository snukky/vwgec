import os
import sys
import yaml

from collections import OrderedDict

sys.path.insert(0, os.path.dirname(__file__))

from preds.prediction_iterator import LDFIterator
from logger import log


class GridSearch(object):
    def __init__(self, evaluator, preds, log_io=None):
        self.evaluator = evaluator
        self.preds = preds
        self.log = log_io

    def run(self, steps=10, levels=1, favor='min'):
        scores = OrderedDict()
        params = self.__param_range(steps)
        log.info("Evaluate params: {}".format(params))

        for thr in params:
            score = self.evaluator.run(thr)
            scores[thr] = score
            log.info("Threshold {:.4f} gives score: {}".format(thr, score))
            if self.log:
                self.log.write("{}\t{}\n".format(thr, score))

        best = self.__best_score(scores)
        log.info("Best: {}".format(best))
        if self.log:
            self.log.write("best:{}\n".format(best))
        return best

    def __best_score(self, scores, favor='min'):
        max_score = max(s[0] for s in scores.values())
        best_scores = OrderedDict(
            [(thr, score) for thr, score in scores.iteritems()
             if score[0] == max_score])
        best = best_scores.keys()[0 if favor == 'min' else -1]
        return (best, best_scores[best])

    def __param_range(self, steps):
        self.preds.seek(0)
        iterator = LDFIterator(self.preds)

        min_thr, max_thr = float('inf'), float('-inf')
        for values in iterator:
            for _, value in values:
                if min_thr > value:
                    min_thr = value
                if max_thr < value:
                    max_thr = value

        log.debug("found min/max params: {}/{}".format(min_thr, max_thr))
        step = (max_thr - min_thr) / float(steps)
        return self.__frange(min_thr, max_thr, step)

    def __frange(self, start, stop, step, eps=0.00001, prec=4):
        values = []
        if start > stop:
            return []
        if start == stop:
            return [round(start, prec)]
        val = start
        while val <= stop + eps:
            values.append(round(val, prec))
            val += step
        return values
