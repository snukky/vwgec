import os
import yaml

ROOT_DIR    = os.path.dirname(os.path.realpath(__file__))
SCRIPTS_DIR = os.path.abspath(os.path.join(ROOT_DIR, '..', 'scripts'))

Config = {}

def load_config(config_file):
    global Config
    with open(config_file, 'r') as config_io:
        try:
            Config = yaml.load(config_io)
            return Config
        except yaml.YAMLError as ex:
            print(ex)
    return Config
