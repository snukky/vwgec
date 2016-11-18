import os
import sys
import yaml

sys.path.insert(0, os.path.dirname(__file__))

from settings import config
from logger import log


def load_config(config_file, updated_configs={}):
    settings.config.load_config(config_file, updated_configs)
