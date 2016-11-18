#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import gecvw
from gecvw.settings import config
from gecvw.logger import log
from gecvw.utils import cmd

import gecvw.features
import gecvw.prediction
import gecvw.evaluation

from gecvw.vw.vw_trainer import VWTrainer
from gecvw.vw.vw_predictor import VWPredictor
from gecvw.evaluation import maxmatch


def main():
    args = parse_user_args()
    gecvw.load_config(args.config, {'source-cset': args.source_cset,
                                    'target-cset': args.target_cset})

    if not os.path.exists(args.work_dir):
        os.makedirs(args.work_dir)
    log.info("work dir: {}".format(args.work_dir))

    cfg_file = args.work_dir + '/config.yml'
    if not os.path.exists(cfg_file):
        shutil.copy(args.config, cfg_file)

    model = cmd.filepath(args.work_dir, config['model']) + '.vw'
    if not os.path.exists(model):
        train_set = cmd.filepath(args.work_dir, 'train')
        cmd.ln(config['train-set'], train_set + '.txt')

        if not config['factors']:
            pass  # add factors

        extract_features(train_set, train=True)
        VWTrainer().train(model, train_set + '.feats')

    thr_file = cmd.filepath(args.work_dir, 'threshold')
    if not os.path.exists(thr_file):
        dev_set = cmd.filepath(args.work_dir, 'dev')
        cmd.ln(config['dev-set'], dev_set + '.m2')

        maxmatch.parallelize_m2(dev_set + '.m2', dev_set + '.txt')

        if not config['factors']:
            pass  # add factors

        extract_features(dev_set, train=False)
        train_vw(model, dev_set)

        search_dir = args.work_dir + '/grid_search'
        if not os.path.exists(search_dir):
            os.makedirs(search_dir)

        threshold = search_threshold(dev_set, work_dir=search_dir)
        with open(thr_file, 'w') as thr_io:
            thr_io.write("{}".format(threshold[0]))
    else:
        with open(thr_file) as thr_io:
            threshold = float(thr_io.read().strip())

    for name, m2 in config['test-sets'].iteritems():
        test_set = cmd.filepath(args.work_dir, name)

        if os.path.exists(test_set + '.eval'):
            continue

        cmd.ln(m2, test_set + '.m2')
        maxmatch.parallelize_m2(test_set + '.m2', test_set + '.txt')

        if not config['factors']:
            pass  # add factors

        extract_features(test_set, train=False)
        run_vw(model, test_set)
        apply_predictions(test_set)

        score = maxmatch.evaluate_m2(test_set + '.out', test_set + '.m2')
        log.info("Results for {}: {}".format(m2, score))


def extract_features(data, train=False):
    with open(data + '.txt') as txt, \
         open(data + '.feats', 'w') as feat, \
         open(data + '.cword', 'w') as cword:
        gecvw.features.extract_features(txt, feat, cword, train=train)


def train_vw(model, data):
    VWPredictor().run(model, data + '.feats', data + '.pred')


def search_threshold(data, work_dir):
    return gecvw.evaluation.run_grid_search(
        data + '.m2', data + '.cword', data + '.pred', work_dir=work_dir)


def apply_predictions(data):
    with open(data + '.txt') as txt, \
            open(data + '.out', 'w') as out, \
            open(data + '.cword', 'r') as cword, \
            open(data + '.pred', 'r') as pred:
        gecvw.prediction.apply_predictions(txt, out, cword, pred)


def run_vw(model, data):
    VWPredictor().run(model, data + '.feats', data + '.pred')


def parse_user_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-1', '--source-cset', help="source confusion set")
    parser.add_argument('-2', '--target-cset', help="target confusion set")
    parser.add_argument(
        '-f', '--config', required=True, help="configuration file")
    parser.add_argument(
        '-w', '--work-dir', required=True, help="working directory")
    return parser.parse_args()


if __name__ == '__main__':
    main()
