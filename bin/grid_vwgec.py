#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import yaml
import itertools

from joblib import Parallel, delayed

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def main():
    args = parse_user_args()

    info("Work dir: {}".format(args.work_dir))
    if not os.path.exists(args.work_dir):
        os.makedirs(args.work_dir)

    updates = config_updates(args.grid_config)
    nums = ["%.2d" % i for i in range(len(updates))]
    info("Test {} configs".format(len(updates)))

    jobs = []
    for num, update in zip(nums, updates):
        info("Model {}: {}".format(num, update))

        config = os.path.join(args.work_dir, "config.{}.yml".format(num))
        workdir = os.path.join(args.work_dir, "model." + num)
        logfile = os.path.join(args.work_dir, "log." + num)

        update_config(args.config, update, config, logfile)

        # run_vwgec(config, workdir)
        jobs.append(delayed(run_vwgec)(config, workdir, num))
    results = Parallel(n_jobs=args.jobs, verbose=100)(jobs)


def update_config(config_in, update, config_out, log_file):
    with open(config_in, 'r') as config_io:
        config = yaml.load(config_io)
        config.update(update)
        config.update({'log-file': log_file})
    with open(config_out, 'w') as config_io:
        yaml.dump(config, config_io, default_flow_style=False)


def config_updates(config_file):
    with open(config_file, 'r') as config_io:
        config = yaml.load(config_io)
    items = [[(k, v) for v in config[k]] for k in config]
    updates = [dict(i) for i in itertools.product(*items)]
    return updates


def run_vwgec(config, work_dir, num=None):
    info("Start {}".format(num))
    os.popen("{}/bin/run_vwgec.py -f {} -w {}".format(ROOT_DIR, config,
                                                      work_dir))
    return True


def info(msg):
    print >> sys.stderr, msg


def parse_user_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--config', required=True, help="configuration file")
    parser.add_argument(
        '-g', '--grid-config', required=True, help="configuration file")
    parser.add_argument(
        '-w', '--work-dir', required=True, help="working directory")
    parser.add_argument('-j', '--jobs', type=int, default=4)
    return parser.parse_args()


if __name__ == '__main__':
    main()
