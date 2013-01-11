from __future__ import with_statement

from chef_solo_cup.helpers import sudo_dry
from chef_solo_cup.log import setup_custom_logger


def gem(args, config, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    logger.info("-> Installing Chef ...")
    sudo_dry('gem install -v {0} ohai --no-rdoc --no-ri'.format(args.ohai_version), args, logger=logger)
    sudo_dry('gem install -v {0} chef --no-rdoc --no-ri'.format(args.chef_version), args, logger=logger)
