# -*- coding: utf-8 -*-

from __future__ import with_statement

from fabric.api import hide, settings
from chef_solo_cup.helpers import add_line_if_not_present_dry
from chef_solo_cup.helpers import rsync_project_dry
from chef_solo_cup.helpers import run_dry
from chef_solo_cup.helpers import sudo_dry
from chef_solo_cup.log import setup_custom_logger


def sync(args, config, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    if args['sync'] == "git":
        # TODO: Allow this to be any host
        add_line_if_not_present_dry(args, '~/.ssh/known_hosts', "github.com,207.97.227.239 ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==", logger=logger)  # noqa
        run_dry(' ; '.join([
            'if [ -d {1}/.git ]',
            'then cd {1} && git pull origin master',
            'else rm -rf {1} && git clone {0} {1}',
            'fi'
        ]).format(
            args['repository'],
            args['chef_file_dest']
        ), args, logger=logger)
    else:
        with settings(hide('stdout'), warn_only=True):
            rsync_exclusions = args['rsync_exclusions']
            if not rsync_exclusions:
                rsync_exclusions = []
            rsync_exclusions.append('.git')

            rsync_project_dry(
                args,
                logger=logger,
                extra_opts="-Caz",
                delete=True,
                exclude=rsync_exclusions,
                local_dir="./",
                remote_dir=args['chef_file_dest'],
                capture=True
            )

    return sudo_dry("chmod -R a+w {0}".format(
        args['chef_file_dest']
    ), args, logger=logger)
