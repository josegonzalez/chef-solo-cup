from __future__ import with_statement

from chef_solo_cup.helpers import sudo_dry
from chef_solo_cup.commands.sync import sync
from chef_solo_cup.log import setup_custom_logger


def update(args, config, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    sync(args, config, logger=logger)

    command = "cd {0} && source /etc/profile && `which chef-solo` -c {0}/{1} -j {0}/{2} -l {3}"
    command += ' && rm -rf {0}'.format(args.chef_file_dest)

    sudo_dry(command.format(args.chef_file_dest, args.config_path, config.get('dna_path'), args.loglevel), args, logger=logger)
