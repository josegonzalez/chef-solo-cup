# -*- coding: utf-8 -*-

from __future__ import with_statement

from chef_solo_cup.log import setup_custom_logger


def inspect(args, config, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    logger.info(config)
