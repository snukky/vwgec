import os
import yaml

from logger import log

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
SCRIPTS_DIR = os.path.abspath(os.path.join(ROOT_DIR, '..', 'scripts'))

REQUIRED_CONFIG_KEYS = [
    'vowpal-wabbit', 'source-cset', 'target-cset', 'factors',
    'features', 'model'
]
OPTIONAL_CONFIG_KEYS = [
    'source-cset', 'target-cset', 'factors', 'word-classes',
    'feature-filter', 'feature-freq', 'threshold', 'nulls-ngrams', 'nulls-min-freq',
    'threads', 'vw-options'
]

ABSOLUTE_PATH_KEYS = [
    'vowpal-wabbit', 'model', 'word-classes', 'nulls-ngrams', 'feature-filter'
]


class Singleton(object):
    _instances = {}

    def __new__(class_, *args, **kwargs):
        if class_ not in class_._instances:
            class_._instances[class_] = super(Singleton, class_).__new__(
                class_, *args, **kwargs)
        return class_._instances[class_]


class GlobalConfig(Singleton):
    def load_config(self, config_file, updated_settings):
        with open(config_file, 'r') as config_io:
            try:
                self.config = yaml.load(config_io)
                self.config.update(self.__filter_nonetypes(updated_settings))
            except yaml.YAMLError as exc:
                log.error("Load config failed: {}".format(exc))
        log.debug("Load config: {}".format(self.config))

    def save_config(self, config_file):
        log.debug("Save config: {}".format(config_file))
        with open(config_file, 'w') as config_io:
            yaml.dump(self.config, config_io, default_flow_style=False)

    def set(self, key, value):
        self.config[key] = value

    def get(self):
        return self.config

    def save_runnable_config(self, config_file):
        log.info("Save runnable config into {}".format(config_file))
        data = {}
        for key in REQUIRED_CONFIG_KEYS:
            if key not in self.config:
                log.error("Missing required key: {}".format(key))
            value = self.config[key]
            if key in ABSOLUTE_PATH_KEYS:
                value = os.path.abspath(value)
            data[key] = value

        for key in OPTIONAL_CONFIG_KEYS:
            if key not in self.config:
                continue
            value = self.config[key]
            if key in ABSOLUTE_PATH_KEYS:
                value = os.path.abspath(value)
            data[key] = value

        with open(config_file, 'w') as config_io:
            yaml.dump(data, config_io)

    def __getitem__(self, key):
        return self.config.get(key, None)

    def __filter_nonetypes(self, config):
        return {key: value
                for key, value in config.iteritems() if value != None}


config = GlobalConfig()
