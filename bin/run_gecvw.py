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

from gecvw import extract_features
from gecvw.vw.vw_trainer import VWTrainer
from gecvw.vw.vw_predictor import VWPredictor
from gecvw.evaluation import maxmatch
from gecvw import run_grid_search
from gecvw import apply_predictions


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
        train_txt = train_set + '.txt'
        train_feats = train_set + '.feats'
        train_cword = train_set + '.cword'

        cmd.ln(config['train-set'], train_txt)
        if not config['factors']:
            pass  # add factors

        extract_features(train_txt, train_feats, train_cword, train=True)
        VWTrainer().train(model, train_feats)

    thr_file = cmd.filepath(args.work_dir, 'threshold')
    if not os.path.exists(thr_file):
        dev_set = cmd.filepath(args.work_dir, 'dev')
        dev_m2 = dev_set + '.m2'
        dev_txt = dev_set + '.txt'
        dev_feats = dev_set + '.feats'
        dev_cword = dev_set + '.cword'
        dev_pred = dev_set + '.pred'

        cmd.ln(config['dev-set'], dev_m2)
        maxmatch.parallelize_m2(dev_m2, dev_txt)

        if not config['factors']:
            pass  # add factors

        extract_features(dev_txt, dev_feats, dev_cword, train=False)
        VWPredictor().run(model, dev_feats, dev_pred)

        search_dir = args.work_dir + '/grid_search'
        if not os.path.exists(search_dir):
            os.makedirs(search_dir)

        threshold = run_grid_search(
            dev_m2, dev_cword, dev_pred, work_dir=search_dir)

        with open(thr_file, 'w') as thr_io:
            thr_io.write("{}".format(threshold[0]))
    else:
        with open(thr_file) as thr_io:
            threshold = float(thr_io.read().strip())

    for m2 in config['test-sets']:
        test_set = cmd.filepath(args.work_dir, 'test')
        test_eval = test_set + '.eval'

        if os.path.exists(test_eval):
            continue

        test_out = test_set + '.out'
        test_m2 = test_set + '.m2'
        test_txt = test_set + '.txt'
        test_feats = test_set + '.feats'
        test_cword = test_set + '.cword'
        test_pred = test_set + '.pred'

        cmd.ln(m2, test_m2)
        maxmatch.parallelize_m2(test_m2, test_txt)

        if not config['factors']:
            pass  # add factors

        extract_features(test_txt, test_feats, test_cword, train=False)
        VWPredictor().run(model, test_feats, test_pred)

        apply_predictions(test_txt, test_out, test_cword, test_pred)
        score = maxmatch.evaluate_m2(test_out, test_m2)
        log.info("Results for {}: {}".format(m2, score))


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
