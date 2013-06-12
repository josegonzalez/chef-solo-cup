from __future__ import with_statement

import os
import re
import sys

from boto.ec2.autoscale import AutoScaleConnection
from fabric.api import run, sudo
from fabric.contrib.project import rsync_project
import boto.ec2

from chef_solo_cup.log import setup_custom_logger


def get_hosts(args, logger=None):
    dna_path = os.path.join(os.path.realpath(os.getcwd()), 'dna')

    hosts = {}

    includes = []
    if args.dna_patterns:
        includes = map(lambda x: re.compile(x), args.dna_patterns)

    excludes = []
    if args.exclude:
        excludes = map(lambda x: re.compile(x), args.exclude)

    for root, sub_folders, files in os.walk(dna_path):
        files = filter(lambda f: ".json" in f, files)
        for f in files:
            path = root.split("/")
            region = path.pop()
            provider = path.pop()
            service = path.pop()

            if len(excludes):
                skip = map(lambda regex: regex.search(f), excludes)
                skip = reduce(lambda x, y: x or y, skip)
                if skip:
                    continue

            if len(includes):
                skip = map(lambda regex: regex.search(f), includes)
                skip = reduce(lambda x, y: x or y, skip)
                if skip is None:
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

    hosts.update(get_asg_hosts(args, dna_path))
    return hosts

def get_asg_hosts(args, dna_path):
    hosts = {}
    for region in args.regions:
        auto_scale_conn = AutoScaleConnection(args.aws_access_key_id, args.aws_secret_access_key)
        conn = boto.ec2.connect_to_region(
            region,
            aws_access_key_id=args.aws_access_key_id,
            aws_secret_access_key=args.aws_secret_access_key,
        )
        for group in auto_scale_conn.get_all_groups():
            instance_ids = [i.instance_id for i in group.instances]
            reservations = conn.get_all_instances(instance_ids)
            instances = [i for r in reservations for i in r.instances]
            for instance in instances:
                name = '{}_{}'.format(group.name, instance.id)
                hosts[name] = {
                    'region': region,
                    'provider': 'AWS',
                    'public_ip': instance.ip_address,
                    'dna_path': os.path.join('asg', group.name)
                }
    return hosts


def rsync_project_dry(args, logger=None, **kwargs):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    if args.dry_run:
        logger.info("[RSYNC_PROJECT] From {0} to {1} with opts='{2}' excluding='{3}'".format(kwargs.get('local_dir'), kwargs.get('remote_dir'), kwargs.get('extra_opts'), kwargs.get('exclude')))
    else:
        out = rsync_project(**kwargs)
        if out.return_code != 0:
            logger.info("[RSYNC_PROJECT] Failed command with status code {0}, please run `chef-solo-cup clean` against this node".format(out.return_code))
            sys.exit(0)


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
