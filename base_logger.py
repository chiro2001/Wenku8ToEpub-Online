import logging
from colorlog import ColoredFormatter


def getLogger(name=__name__):
    logger_base = logging.getLogger(name)
    logger_base.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()

    color_formatter = ColoredFormatter('%(log_color)s[%(module)-15s][%(funcName)-20s][%(levelname)-8s] %(message)s')

    # formatter = logging.Formatter('[%(module)-15s][%(funcName)-7s][%(levelname)-8s] %(message)s')
    stream_handler.setFormatter(color_formatter)

    logger_base.addHandler(stream_handler)

    return logger_base


if __name__ == '__main__':
    logger = getLogger(__name__)
    logger.debug('debug message')
    logger.info('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')