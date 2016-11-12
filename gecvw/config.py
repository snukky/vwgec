import os
import yaml

ROOT_DIR    = os.path.dirname(os.path.realpath(__file__))
SCRIPTS_DIR = os.path.abspath(os.path.join(ROOT_DIR, '..', 'scripts'))

CONFIG = {}

def load_config(config_file):
    global CONFIG
    with open(config_file, 'r') as config_io:
        try:
            CONFIG = yaml.load(config_io)
            return CONFIG
        except yaml.YAMLError as ex:
            print(ex)
    return CONFIG
