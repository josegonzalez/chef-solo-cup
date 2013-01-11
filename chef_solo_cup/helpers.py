from __future__ import with_statement

from fabric.api import run, sudo
from fabric.contrib.project import rsync_project
from chef_solo_cup.log import setup_custom_logger
import os


def get_hosts(args, logger=None):
    dna_path = os.path.join(os.path.realpath(os.getcwd()), 'dna')

    hosts = {}

    for root, sub_folders, files in os.walk(dna_path):
        files = filter(lambda f: ".json" in f, files)
        for f in files:
            path = root.split("/")
            region = path.pop()
            provider = path.pop()
            service = path.pop()

            if args.dna_patterns:
                skip = True
                for dna in args.dna_patterns:
                    if dna in f:
                        skip = False

                if skip:
                    continue

            if args.regions and region not in args.regions:
                continue
            if args.providers and provider not in args.providers:
                continue
            if args.services and service not in args.services:
                continue

            host = f.replace(".json", "")

            if host in ["all", "default"]:
                continue

            hosts[host] = {
                'file': f,
                'path': os.path.join(root, f),
                'root': root,
                'region': region,
                'provider': provider,
                'service': service,
                'dna_path': "{0}/{1}/{2}/{3}".format(service, provider, region, f)
            }

    return hosts


def rsync_project_dry(args, logger=None, **kwargs):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    if args.dry_run:
        logger.info("[RSYNC_PROJECT] {0}".format(**kwargs))
    else:
        rsync_project(**kwargs)


def run_dry(cmd, args, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    if args.dry_run:
        logger.info("[RUN] {0}".format(cmd))
    else:
        return run(cmd)


def sudo_dry(cmd, args, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    if args.dry_run:
        logger.info("[SUDO] {0}".format(cmd))
    else:
        return sudo(cmd)


def add_line_if_not_present_dry(args, filename, line, run_f=run, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    cmd = "grep -q -e '%s' %s || echo '%s' >> %s" % (line, filename, line, filename)
    if args.dry_run:
        logger.info("[SUDO] {0}".format(cmd))
    else:
        run_f(cmd)
