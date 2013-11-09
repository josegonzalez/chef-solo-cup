from __future__ import with_statement

import collections
import os
import re
import itertools
import sys

from boto.ec2 import connect_to_region
from boto.exception import EC2ResponseError
import boto.ec2.autoscale
from fabric.api import run, sudo
from fabric.contrib.project import rsync_project

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

    all_hosts = itertools.chain(
        get_filesystem_hosts(args, dna_path),
        get_asg_hosts(args, dna_path),
    )

    for host, data in all_hosts:
        f = data.get('file', '')
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

        if args.regions and data.get('region') not in args.regions:
            continue
        if args.providers and data.get('provider') not in args.providers:
            continue
        if args.services and data.get('service') not in args.services:
            continue
        hosts[host] = data

    hosts = collections.OrderedDict(sorted(hosts.items()))

    if args.quantity is not None:
        x = itertools.islice(hosts.items(), 0, int(args.quantity))
        hosts = {}
        for key, value in x:
            hosts[key] = value

        hosts = collections.OrderedDict(sorted(hosts.items()))

    return hosts


def get_filesystem_hosts(args, dna_path):
    for root, sub_folders, files in os.walk(dna_path):
        files = filter(lambda f: ".json" in f, files)
        for f in files:
            path = root.split("/")
            region = path.pop()
            provider = path.pop()
            service = path.pop()

            host = f.replace(".json", "")

            if host in ["all", "default"]:
                continue

            yield host, {
                'file': f,
                'path': os.path.join(root, f),
                'root': root,
                'region': region,
                'provider': provider,
                'service': service,
                'dna_path': "dna/{0}/{1}/{2}/{3}".format(service, provider, region, f)
            }


def get_asg_hosts(args, dna_path):
    if not args.regions:
        return

    if not args.aws_access_key_id or not args.aws_secret_access_key:
        return

    for region in args.regions:
        auto_scale_conn = boto.ec2.autoscale.connect_to_region(
            region,
            aws_access_key_id=args.aws_access_key_id,
            aws_secret_access_key=args.aws_secret_access_key,
        )
        conn = connect_to_region(
            region,
            aws_access_key_id=args.aws_access_key_id,
            aws_secret_access_key=args.aws_secret_access_key,
        )

        asg_path = os.path.join(os.path.realpath(os.getcwd()), args.asg_dna_path)
        asg_dna_files = [ f for f in os.listdir(asg_path) if os.path.isfile(os.path.join(asg_path, f)) ]

        for group in auto_scale_conn.get_all_groups():
            instance_ids = [i.instance_id for i in group.instances]
            if not instance_ids:
                continue

            try:
                reservations = conn.get_all_instances(instance_ids)
            except EC2ResponseError:
                continue

            group_dna_file = None
            for asg_dna_file in asg_dna_files:
                if asg_dna_file == group.name:
                    group_dna_file = asg_dna_file

                group_name_json = group.name + ".json"
                if asg_dna_file == group_name_json:
                    group_dna_file = asg_dna_file

            if not group_dna_file:
                for asg_dna_file in asg_dna_files:
                    if group.name.startswith(asg_dna_file):
                        group_dna_file = asg_dna_file

            if not group_dna_file:
                group_dna_file = group.name

            instances = [i for r in reservations for i in r.instances]
            for instance in instances:
                name = '{0}_{1}'.format(group.name, instance.id)
                yield name, {
                    'file': name,
                    'region': region,
                    'provider': 'AWS',
                    'public_ip': instance.ip_address,
                    'dna_path': os.path.join(args.asg_dna_path, group_dna_file),
                }


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
