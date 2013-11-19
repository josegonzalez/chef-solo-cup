import argparse
import logging


logging.basicConfig()


def setup_custom_logger(name, args=None, output=None, formatter=None):
    logger = logging.getLogger(name)
    logger.propagate = False
    if logger.handlers:
        logger.handlers = []

    has_args = args is not None and type(args) == argparse.Namespace
    is_debug = has_args and args.debug == True

    if not logger.handlers:
        if formatter is None:
            formatter = logging.Formatter('[%(asctime)s] %(levelname)-7s %(message)s')

        handler = logging.StreamHandler()
        if output is None and has_args:
            output = args.output

        if output is not None:
            handler = logging.FileHandler(output)

        if formatter is not False:
            handler.setFormatter(formatter)

        logger.addHandler(handler)

    if is_debug:
        logger.setLevel(logging.DEBUG)
        if hasattr(logging, 'captureWarnings'):
            logging.captureWarnings(True)
    else:
        logger.setLevel(logging.INFO)
        if hasattr(logging, 'captureWarnings'):
            logging.captureWarnings(False)

    logger.debug('Logger level is {0}'.format(logging.getLevelName(logger.level)))

    return logger
