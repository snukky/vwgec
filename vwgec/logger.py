import logging

LOG_LEVELS = {
    'error': logging.ERROR,
    'warn': logging.WARN,
    'info': logging.INFO,
    'debug': logging.DEBUG
}


def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)+7s | %(module)-11s | %(message)s',
            datefmt="%d.%m.%y %H:%M:%S")

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.propagate = False

    return logger


def set_level(level='info', name='root'):
    logging.getLogger(name).setLevel(LOG_LEVELS[level.lower()])


log = setup_logger('root')
