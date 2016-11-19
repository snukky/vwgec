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
import gecvw.factors

from gecvw.vw.vw_trainer import VWTrainer
from gecvw.vw.vw_predictor import VWPredictor
from gecvw.evaluation import maxmatch

THRESHOLD_FILE = 'threshold.txt'


def main():
    args = parse_user_args()
    gecvw.load_config(args.config, {'source-cset': args.source_cset,
                                    'target-cset': args.target_cset})

    log.info("Work dir: {}".format(args.work_dir))
    if not os.path.exists(args.work_dir):
        os.makedirs(args.work_dir)
        os.makedirs(args.work_dir + '/train')
        os.makedirs(args.work_dir + '/dev')
        os.makedirs(args.work_dir + '/gridsearch')

    cfg_file = args.work_dir + '/config.yml'
    if not os.path.exists(cfg_file):
        shutil.copy(args.config, cfg_file)

    model = cmd.filepath(args.work_dir, config['model']) + '.vw'
    if not os.path.exists(model):
        log.info("Start training...")

        train_set = args.work_dir + '/train/train'
        cmd.ln(config['train-set'], train_set + '.txt')

        extract_features(train_set, train=True, factors=config['factors'])
        VWTrainer().train(model, train_set + '.feats')

    thr_value = read_threshold(args.work_dir)
    if not thr_value:
        log.info("Start grid search...")

        dev_set = args.work_dir + '/dev/dev'
        cmd.ln(config['dev-set'], dev_set + '.m2')
        parallelize_m2(dev_set)

        extract_features(dev_set, train=False, factors=config['factors'])
        train_vw(model, dev_set)

        thr_value, _ = search_threshold(
            dev_set, work_dir=args.work_dir + '/gridsearch')
        save_threshold(args.work_dir, thr_value)

    for name, m2 in config['test-sets'].iteritems():
        log.info("Start evaluation for '{}'...".format(name))

        test_set = cmd.filepath(args.work_dir, name)
        if os.path.exists(test_set + '.eval'):
            continue

        cmd.ln(m2, test_set + '.m2')
        parallelize_m2(test_set)

        extract_features(test_set, train=False, factors=config['factors'])
        run_vw(model, test_set)
        apply_predictions(test_set)

        score = maxmatch.evaluate_m2(test_set + '.out', test_set + '.m2')
        log.info("Results for {}: {}".format(m2, score))


def extract_features(data, train=False, factors={}):
    needed_factors = factors.keys()
    if train:
        needed_factors = [fn for fn, ff in factors.iteritems() if not ff]
    if needed_factors:
        new_factors = gecvw.factors.factorize_file(data + '.txt',
                                                   needed_factors)
        factors.update(new_factors)

    with open(data + '.txt') as txt, \
         open(data + '.feats', 'w') as feat, \
         open(data + '.cword', 'w') as cword:
        gecvw.features.extract_features(
            txt, feat, cword, train=train, factor_files=factors)


def train_vw(model, data):
    VWPredictor().run(model, data + '.feats', data + '.pred')


def read_threshold(work_dir):
    thr_file = os.path.join(work_dir, THRESHOLD_FILE)
    if not os.path.exists(thr_file):
        return None
    with open(thr_file) as thr_io:
        value = float(thr_io.read().strip())
    return value


def search_threshold(data, work_dir):
    return gecvw.evaluation.run_grid_search(
        data + '.m2', data + '.cword', data + '.pred', work_dir=work_dir)


def save_threshold(work_dir, value):
    with open(os.path.join(work_dir, THRESHOLD_FILE), 'w') as thr_io:
        thr_io.write(str(value))


def apply_predictions(data):
    with open(data + '.txt') as txt, \
            open(data + '.out', 'w') as out, \
            open(data + '.cword', 'r') as cword, \
            open(data + '.pred', 'r') as pred:
        gecvw.prediction.apply_predictions(txt, out, cword, pred)


def parallelize_m2(data):
    maxmatch.parallelize_m2(data + '.m2', data + '.txt')


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
