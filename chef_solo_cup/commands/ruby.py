# -*- coding: utf-8 -*-

from __future__ import with_statement

from chef_solo_cup.helpers import sudo_dry
from chef_solo_cup.log import setup_custom_logger


def ruby(args, config, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    logger.info("-> Installing Ruby 1.9.2")
    return sudo_dry("apt-get install -y {0}".format(' '.join([
        'ruby1.9.1',
        'ruby1.9.1-dev',
        'rubygems1.9.1',
        'irb1.9.1',
        'ri1.9.1',
        'rdoc1.9.1',
        'libopenssl-ruby1.9.1',
    ])), args, logger=logger)
