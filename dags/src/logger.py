import logging

logging.basicConfig(level=logging.INFO)


def make_logger(
    name,
):
    # util method to make a logger
    logger = logging.getLogger(name)
    return logger
