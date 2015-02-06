# -*- coding: utf-8 -*-

from __future__ import with_statement

from chef_solo_cup.helpers import sudo_dry
from chef_solo_cup.log import setup_custom_logger


def gem(args, config, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    logger.info("-> Installing Chef ...")
    gem_install_command = 'gem install -v {0} {1} --no-rdoc --no-ri'
    sudo_dry(gem_install_command.format(
        args['ohai_version'],
        'ohai'
    ), args, logger=logger)
    return sudo_dry(gem_install_command.format(
        args['chef_version'],
        'chef'
    ), args, logger=logger)
