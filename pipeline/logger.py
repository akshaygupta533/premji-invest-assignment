import logging

logging.basicConfig(level=logging.INFO)


def make_logger(
    name,
):
    logger = logging.getLogger(name)
    return logger
