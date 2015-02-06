# -*- coding: utf-8 -*-

from __future__ import with_statement

from fabric.api import hide, settings
from chef_solo_cup.helpers import sudo_dry
from chef_solo_cup.log import setup_custom_logger
from chef_solo_cup.commands.gem import gem
from chef_solo_cup.commands.ruby import ruby


def bootstrap(args, config, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
        result = sudo_dry("command -v chef-solo", args, logger=logger)

    if not result.failed:
        logger.info("-> Chef already boostrapped.")
        return

    logger.info("-> Installing Prerequisite Packages...")
    sudo_dry("apt-get update", args, logger=logger)
    sudo_dry("apt-get upgrade -y", args, logger=logger)
    sudo_dry("apt-get update", args, logger=logger)
    sudo_dry("apt-get install -y {0}".format(' '.join([
        'autoconf',
        'binutils-doc',
        'bison',
        'build-essential',
        'curl',
        'flex',
        'gcc',
        'git-core',
        'libreadline-dev',
        'libssl-dev',
        'libtool',
        'libxml2-dev',
        'libxslt-dev',
        'zlib1g-dev',
    ])), args, logger=logger)

    ruby(args, config, logger=logger)

    gem(args, config, logger=logger)
