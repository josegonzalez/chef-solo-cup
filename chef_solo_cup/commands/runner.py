from __future__ import with_statement

from chef_solo_cup.helpers import run_dry, sudo_dry
from chef_solo_cup.log import setup_custom_logger


def run_command(args, config, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    run_dry(args.cmd, args, logger=logger)


def sudo_command(args, config, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    sudo_dry(args.cmd, args, logger=logger)
