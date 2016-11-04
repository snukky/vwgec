import logging


def setup_logger(name):
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)+7s | %(module)-11s | %(message)s',
        datefmt="%d.%m.%y %H:%M:%S")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    return logger


log = setup_logger('root')
