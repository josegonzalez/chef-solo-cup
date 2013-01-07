from __future__ import with_statement

from chef_solo_cup.helpers import sudo_dry
from chef_solo_cup.commands.sync import sync
from chef_solo_cup.log import setup_custom_logger


def default(args, config, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    sync(args, config, logger=logger)
    sudo_dry("source /etc/profile && `which chef-solo` -c {0}/solo-config.rb -j {0}/dna/{1} -l {2}".format(args.chef_file_dest, "default.json", args.loglevel), args, logger=logger)
