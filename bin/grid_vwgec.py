#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import yaml
import itertools

from joblib import Parallel, delayed

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import vwgec
from vwgec.settings import config
from vwgec.logger import log


def main():
    args = parse_user_args()

    log.info("Work dir: {}".format(args.work_dir))
    if not os.path.exists(args.work_dir):
        os.makedirs(args.work_dir)

    updates = config_updates(args.grid_config)
    nums = ["%.2d" % i for i in range(len(updates))]
    log.info("Test {} config updates".format(len(updates)))

    jobs = []
    for num, update in zip(nums, updates):
        log.info("Update config with: {}".format(update))
        vwgec.load_config(args.config, update)

        config = os.path.join(args.work_dir, "config.{}.yml".format(num))
        vwgec.config.save_config(config)
        workdir = os.path.join(args.work_dir, "model." + num)
        log = os.path.join(args.work_dir, "log." + num)

        # run_vwgec(config, workdir)
        jobs.append(delayed(run_vwgec)(config, workdir, log))
    Parallel(n_jobs=args.jobs, verbose=False)(jobs)


def config_updates(config_file):
    with open(config_file, 'r') as config_io:
        config = yaml.load(config_io)
    items = [[(k, v) for v in config[k]] for k in config]
    updates = [dict(i) for i in itertools.product(*items)]
    return updates


def run_vwgec(config, work_dir, log_file):
    os.popen("{}/bin/run_vwgec.py -f {} -w {} &> {}" \
        .format(vwgec.settings.ROOT_DIR, config, work_dir, log_file))


def parse_user_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--config', required=True, help="configuration file")
    parser.add_argument('-g', '--grid-config', required=True, help="configuration file")
    parser.add_argument('-w', '--work-dir', required=True, help="working directory")
    parser.add_argument('-j', '--jobs', default=4)
    return parser.parse_args()


if __name__ == '__main__':
    main()
