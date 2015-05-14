# -*- coding: utf-8 -*-

# https://www.opscode.com/chef/install.sh | sudo bash -s -- -v 11.16.4-1


from __future__ import with_statement

from chef_solo_cup.helpers import sudo_dry
from chef_solo_cup.log import setup_custom_logger


def chef(args, config, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    install_url = 'curl -sSL https://www.opscode.com/chef/install.sh'
    install_command = '{0} | sudo bash -s -- -v {1}'.format(
        install_url, args['chef_version']
    )
    uninstall_command = 'gem uninstall -a chef ohai'

    logger.info("-> Installing Chef ...")
    response = sudo_dry(uninstall_command, args, logger=logger)
    if response:
        return sudo_dry(install_command, args, logger=logger)
    return response
