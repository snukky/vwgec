import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from vwgec.settings import config
from prediction.prediction_reader import PredictionReader
from prediction.output_formatter import OutputFormatter

from logger import log


def apply_predictions(txt_io, out_io, cword_io, pred_io, threshold):
    log.info("Apply predictions with threshold= {}".format(threshold))
    reader = PredictionReader(
        txt_io, cword_io, pred_io, cset=config['target-cset'])
    formatter = OutputFormatter(out_io, threshold=threshold)

    for sid, sentence, preds in reader:
        formatter.format(sid, sentence.strip(), preds)
