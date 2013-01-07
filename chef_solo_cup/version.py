import logging
import sys

from chef_solo_cup import __version__
from chef_solo_cup.log import setup_custom_logger


def version(args):
    if args.version:
        formatter = logging.Formatter('%(message)s')
        logger = setup_custom_logger('chef-solo-cup', args=args, formatter=formatter)
        logger.info('Chef Solo Cup {0}'.format(__version__))
        sys.exit(0)
