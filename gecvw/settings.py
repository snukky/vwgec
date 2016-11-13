import os
import yaml

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
SCRIPTS_DIR = os.path.abspath(os.path.join(ROOT_DIR, '..', 'scripts'))

from logger import log


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

    def get(self):
        return self.config

    def __getitem__(self, key):
        return self.config[key]

    def __filter_nonetypes(self, config):
        return {key: value
                for key, value in config.iteritems() if value != None}


config = GlobalConfig()
