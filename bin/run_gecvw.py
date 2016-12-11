#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import vwgec
from vwgec.settings import config
from vwgec.logger import log
from vwgec.utils import cmd

import vwgec.features
import vwgec.prediction
import vwgec.evaluation
import vwgec.evaluation.maxmatch
import vwgec.utils.tokenization
import vwgec.factors

from vwgec.vw.vw_trainer import VWTrainer
from vwgec.vw.vw_predictor import VWPredictor

THRESHOLD_FILE = 'threshold.txt'


def main():
    args = parse_user_args()
    # update = {'source-cset': args.source_cset, 'target-cset': args.target_cset}
    update = {}
    vwgec.load_config(args.config, update)

    log.info("Work dir: {}".format(args.work_dir))
    if not os.path.exists(args.work_dir):
        os.makedirs(args.work_dir)

    if config['train']:
        if not os.path.exists(args.work_dir + '/train'):
            os.makedirs(args.work_dir + '/train')

        cfg_file = args.work_dir + '/config.yml'
        if not os.path.exists(cfg_file):
            shutil.copy(args.config, cfg_file)

    if config['train']:
        model = cmd.filepath(args.work_dir, config['model'], noext=False)
        config.set('model', model)
        if config['feature-filter']:
            feat_set = cmd.filepath(
                args.work_dir, config['feature-filter'], noext=False)
            config.set('feature-filter', feat_set)

    model = config['model']
    log.info("Model: {}".format(model))
    feat_set = config['feature-filter']
    log.info("Feature filter: {}".format(feat_set))

    if config['train'] and not os.path.exists(model):
        log.info("Start training...")

        train_set = args.work_dir + '/train/train'
        for train_data in config['train-set']:
            cmd.run("cat {} >> {}".format(train_data, train_set + '.txt'))

        extract_features(
            train_set, train=True, factors=config['factors'], freqs=feat_set)
        VWTrainer().train(model, train_set + '.feats')

    thr_value = config['threshold'] or 0.0
    if config['train']:
        thr_value = read_threshold(args.work_dir) or thr_value
        if not config['dev-set']:
            log.info("No development set, using threshold= {}".format(
                thr_value))

    if config['train'] and config['dev-set'] and not thr_value:
        if not os.path.exists(args.work_dir + '/dev'):
            os.makedirs(args.work_dir + '/dev')
        if not os.path.exists(args.work_dir + '/gridsearch'):
            os.makedirs(args.work_dir + '/gridsearch')

        log.info("Start tuning...")

        dev_set = args.work_dir + '/dev/dev'
        cmd.ln(config['dev-set'], dev_set + '.m2')
        parallelize_m2(dev_set)

        extract_features(
            dev_set, train=False, factors=config['factors'], freqs=feat_set)
        train_vw(model, dev_set)

        thr_value, _ = search_threshold(
            dev_set, work_dir=args.work_dir + '/gridsearch')
        save_threshold(args.work_dir, thr_value)
        config.set('threshold', thr_value)

    if config['train'] and config['train-set']:
        config.save_runnable_config(args.work_dir + '/run.yml')

    if config['test-sets']:
        for name, m2 in config['test-sets'].iteritems():
            test_set = cmd.filepath(args.work_dir, name)
            if os.path.exists(test_set + '.eval'):
                continue

            log.info("Start evaluation for '{}'...".format(name))
            cmd.ln(m2, test_set + '.m2')
            parallelize_m2(test_set)

            extract_features(
                test_set,
                train=False,
                factors=config['factors'],
                freqs=feat_set)
            run_vw(model, test_set)
            apply_predictions(test_set, thr_value)
            evaluate_m2(test_set)

        for name, m2 in config['test-sets'].iteritems():
            test_set = cmd.filepath(args.work_dir, name)
            with open(test_set + '.eval') as test_io:
                result = test_io.read().strip()
            log.info("Scores for '{}':\n{}".format(name, result))

    if args.run:
        run_set = cmd.filepath(args.work_dir, args.run)
        cmd.ln(args.run, run_set + '.txt')

        extract_features(
            run_set, train=False, factors=config['factors'], freqs=feat_set)
        run_vw(model, run_set)
        apply_predictions(run_set, thr_value)


def extract_features(data, train=False, factors={}, freqs=None):
    needed_factors = factors.keys()
    if train:
        needed_factors = [fn for fn, ff in factors.iteritems() if not ff]
    if needed_factors:
        new_factors = vwgec.factors.factorize_file(data + '.txt',
                                                   needed_factors)
        factors.update(new_factors)

    with open(data + '.txt') as txt, \
         open(data + '.feats', 'w') as feat, \
         open(data + '.cword', 'w') as cword:
        vwgec.features.extract_features(
            txt, feat, cword, train=train, factor_files=factors)

    if freqs:
        train_freqs = data + '.feats' if train else None
        vwgec.features.filter_features(
            freqs, data + '.feats', create_from=train_freqs)


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
    return vwgec.evaluation.run_grid_search(
        data + '.m2',
        data + '.cword',
        data + '.pred',
        work_dir=work_dir,
        log_file=data + '.grid')


def save_threshold(work_dir, value):
    with open(os.path.join(work_dir, THRESHOLD_FILE), 'w') as thr_io:
        thr_io.write(str(value))


def apply_predictions(data, threshold):
    with open(data + '.txt') as txt, \
            open(data + '.out', 'w') as out, \
            open(data + '.cword', 'r') as cword, \
            open(data + '.pred', 'r') as pred:
        vwgec.prediction.apply_predictions(
            txt, out, cword, pred, threshold=threshold)


def parallelize_m2(data):
    vwgec.evaluation.maxmatch.parallelize_m2(data + '.m2', data + '.tok.txt')
    cmd.run("cut -f1 {f}.tok.txt > {f}.tok.in".format(f=data))
    vwgec.utils.tokenization.convert_tok(data + '.tok.in', data + '.in',
                                         'nltk-moses')
    cmd.run("cut -f2 {f}.tok.txt > {f}.tok.cor".format(f=data))
    vwgec.utils.tokenization.convert_tok(data + '.tok.cor', data + '.cor',
                                         'nltk-moses')
    cmd.run("paste {f}.in {f}.cor > {f}.txt".format(f=data))


def run_vw(model, data):
    VWPredictor().run(model, data + '.feats', data + '.pred')


def evaluate_m2(data):
    vwgec.utils.tokenization.convert_tok(data + '.out', data + '.tok.out',
                                         'moses-nltk')
    vwgec.utils.tokenization.restore_tok(data + '.tok.out', data + '.tok.in',
                                         data + '.sys')
    score = vwgec.evaluation.maxmatch.evaluate_m2(
        data + '.sys', data + '.m2', log_file=data + '.eval')
    log.info("Results for {}: {}".format(data, score))


def parse_user_args():
    parser = argparse.ArgumentParser()
    # parser.add_argument('-1', '--source-cset', help="source confusion set")
    # parser.add_argument('-2', '--target-cset', help="target confusion set")
    parser.add_argument(
        '-f', '--config', required=True, help="configuration file")
    parser.add_argument(
        '-w', '--work-dir', required=True, help="working directory")
    parser.add_argument('-r', '--run', help="file to be corrected")
    parser.add_argument('-o', '--output', help="corrected file")
    return parser.parse_args()


if __name__ == '__main__':
    main()
