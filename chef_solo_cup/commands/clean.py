from __future__ import with_statement

from chef_solo_cup.helpers import sudo_dry
from chef_solo_cup.log import setup_custom_logger


def clean(args, config, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    sudo_dry('rm -rf {0}'.format(args.chef_file_dest), args, logger=logger)
