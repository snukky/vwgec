import os
import yaml

ROOT_DIR    = os.path.dirname(os.path.realpath(__file__))
SCRIPTS_DIR = os.path.abspath(os.path.join(ROOT_DIR, '..', 'scripts'))

def load(config_file):
    with open(config_file, 'r') as config_io:
        try:
            return yaml.load(config_io)
        except yaml.YAMLError as ex:
            print(exc)
    return None
