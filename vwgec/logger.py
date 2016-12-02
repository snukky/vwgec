import logging


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


log = setup_logger('root')
