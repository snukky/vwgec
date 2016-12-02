import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from vwgec.settings import config
from evaluation.grid_search import GridSearch
from evaluation.m2 import M2Evaluator
from logger import log


def run_grid_search(m2_file, cwords, preds, work_dir):
    evaluator = M2Evaluator(m2_file, cwords, preds, work_dir=work_dir)
    searcher = GridSearch(evaluator, preds)
    return searcher.run()
