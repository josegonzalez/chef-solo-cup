# -*- coding: utf-8 -*-

from __future__ import with_statement

import base64
import collections
import itertools
import json
import os
import re
import sys
import unidecode
import urllib2

from boto.ec2 import connect_to_region
from boto.exception import EC2ResponseError
import boto.ec2.autoscale
from fabric.api import run, sudo
from fabric.contrib.project import rsync_project

from chef_solo_cup.log import setup_custom_logger


def get_hosts(args, logger=None):
    dna_path = os.path.join(os.path.realpath(os.getcwd()), 'dna')

    includes = []
    if args['dna_patterns']:
        includes = map(lambda x: re.compile(x, re.I), args['dna_patterns'])

    excludes = []
    if args['exclude']:
        excludes = map(lambda x: re.compile(x, re.I), args['exclude'])

    all_hosts = itertools.chain(
        get_filesystem_hosts(args, dna_path, logger=logger),
        get_asg_hosts(args, dna_path, logger=logger),
    )

    hosts = _collect_valid_hosts(
        all_hosts,
        excludes,
        includes,
        args,
        logger=logger
    )
    hosts = filter_hosts(args, hosts, logger=logger)
    hosts = collections.OrderedDict(sorted(hosts.items()))

    if args['quantity'] is not None:
        x = itertools.islice(hosts.items(), 0, int(args['quantity']))
        hosts = {}
        for key, value in x:
            hosts[key] = value

        hosts = collections.OrderedDict(sorted(hosts.items()))

    return hosts


def _collect_valid_hosts(all_hosts, excludes, includes, args, logger=None):
    hosts = {}
    for host, data in all_hosts:
        if _skip_host(data, excludes, includes, args, logger=logger):
            continue

        if 'public_ip' in data and not data['public_ip']:
            del data['public_ip']
        if 'private_ip' in data and not data['private_ip']:
            del data['private_ip']

        data['host'] = host
        valid_hosts = [data.get('public_ip'), data.get('private_ip'), host]
        for hostname in valid_hosts:
            if hostname:
                data['host'] = hostname
                break

        hosts[host] = data

    return hosts


def _skip_host(data, excludes, includes, args, logger=None):
    f = data.get('file', '')

    for key, value in _resolve_tags(args).iteritems():
        if value != data.get('tags', {}).get(key, None):
            logger.debug('Skipping {0} because tags dont match'.format(f))
            return True

    if len(excludes):
        skip = map(lambda regex: regex.search(f), excludes)
        skip = reduce(lambda x, y: x or y, skip)
        if skip:
            logger.debug('Skipping {0} because exclusion rule'.format(f))
            return True

    if len(includes):
        skip = map(lambda regex: regex.search(f), includes)
        skip = reduce(lambda x, y: x or y, skip)
        if skip is None:
            logger.debug('Skipping {0} because inclusion rule'.format(f))
            return True

    if args['regions'] and data.get('region') not in args['regions']:
        logger.debug('Skipping {0} because regions dont match'.format(f))
        return True
    if args['providers'] and data.get('provider') not in args['providers']:
        logger.debug('Skipping {0} because providers dont match'.format(f))
        return True
    if args['services'] and data.get('service') not in args['services']:
        logger.debug('Skipping {0} because services dont match'.format(f))
        return True
    return False


def _resolve_tags(args):
    if not args.get('tags', None):
        return {}

    tags = {}
    for tag in args.get('tags', {}):
        key, value = tag.split('=')
        tags[key] = value
    return tags


def get_filesystem_hosts(args, dna_path, logger=None):
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
                'tags': {},
                'dna_path': "dna/{0}/{1}/{2}/{3}".format(
                    service,
                    provider,
                    region,
                    f
                )
            }


def get_asg_hosts(args, dna_path, logger=None):
    if not args['regions']:
        return

    if not args['aws_access_key_id'] or not args['aws_secret_access_key']:
        return

    cwd = os.path.realpath(os.getcwd())
    asg_path = os.path.join(cwd, args['asg_dna_path'])

    asg_dna_files = []
    for f in os.listdir(asg_path):
        if os.path.isfile(os.path.join(asg_path, f)):
            asg_dna_files.append(f)

    response = _get_api_response(args, region=None, logger=logger)
    if response:
        for region in args['regions']:
            groups = _group_from_region(response, region)
            for group, instances in groups.items():
                group_name = group.strip()
                if args['use_alternate_databag']:
                    group_dna_file = _get_group_dna_file(
                        args['use_alternate_databag'],
                        asg_dna_files)
                else:
                    group_dna_file = _get_group_dna_file(
                        group_name,
                        asg_dna_files)

                logger.debug('== [group:{0}] [use_alternate_databag:{1}] [databag:{2}]'.format(
                    group,
                    args['use_alternate_databag'],
                    group_dna_file))

                for name, instance in instances.items():
                    yield name, {
                        'file': slugify(name.strip()),
                        'region': region,
                        'provider': 'AWS',
                        'private_ip': instance['private_ip_address'],
                        'public_ip': instance['ip_address'],
                        'group_name': instance['tags']['aws:autoscaling:groupName'],  # noqa
                        'tags': instance['tags'],
                        'dna_path': os.path.join(
                            args['asg_dna_path'],
                            dna_file_name_from_tags(
                                args,
                                group_dna_file.strip(),
                                instance['tags'])
                        ),
                    }
    else:
        for region in args['regions']:
            auto_scale_conn = _connection_autoscale(args, region)
            conn = _connection_ec2(args, region)

            for group in auto_scale_conn.get_all_groups():
                instance_ids = [i.instance_id for i in group.instances]
                if not instance_ids:
                    continue

                try:
                    reservations = conn.get_all_instances(instance_ids)
                except EC2ResponseError:
                    continue

                group_name = group.name.strip()
                if args['use_alternate_databag']:
                    group_dna_file = _get_group_dna_file(
                        args['use_alternate_databag'],
                        asg_dna_files)
                else:
                    group_dna_file = _get_group_dna_file(
                        group_name,
                        asg_dna_files)

                instances = [i for r in reservations for i in r.instances]
                for instance in instances:
                    name = '{0}-{1}'.format(group_name, instance.id)
                    yield name, {
                        'file': slugify(name.strip()),
                        'region': region,
                        'provider': 'AWS',
                        'public_ip': instance.ip_address,
                        'private_ip': instance['private_ip_address'],
                        'group_name': instance['tags']['aws:autoscaling:groupName'],  # noqa
                        'tags': instance['tags'],
                        'dna_path': os.path.join(
                            args['asg_dna_path'],
                            dna_file_name_from_tags(
                                args,
                                group_dna_file.strip(),
                                instance['tags'])
                        ),
                    }


def _group_from_region(response, region):
    groups = {}
    for group, instances in response.items():
        in_region = False
        for name, instance in instances.items():
            in_region = instance['region'] == region
            break

        if not in_region:
            continue
        groups[group] = {}
        for name, instance in instances.items():
            groups[group][name] = instance

    return groups


def _connection_autoscale(args, region):
    return boto.ec2.autoscale.connect_to_region(
        region,
        aws_access_key_id=args['aws_access_key_id'],
        aws_secret_access_key=args['aws_secret_access_key'],
    )


def _connection_ec2(args, region):
    return connect_to_region(
        region,
        aws_access_key_id=args['aws_access_key_id'],
        aws_secret_access_key=args['aws_secret_access_key'],
    )


def _get_api_response(args, region=None, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    if not args['api_url']:
        return None

    request_url = '{0}/nodes/group?status={1}'.format(
        args['api_url'],
        'running'
    )
    if region is not None:
        request_url = '{0}&region={1}'.format(request_url, region)

    request = urllib2.Request(request_url)

    has_username = 'api_username' in args
    has_password = 'api_password' in args
    if has_username and has_password:
        base64string = base64.encodestring('{0}:{1}'.format(
            args['api_username'], args['api_password']
        )).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)

    result = urllib2.urlopen(request)

    if int(result.getcode()) not in [200, 201, 204]:
        error = 'Bad response from api'
        try:
            data = json.loads(result.read())
            error = data.get('message', 'Bad response from api')
        except:
            pass
        logger.error(error)
        sys.exit(1)

    response = None
    try:
        response = json.loads(result.read())
    except ValueError:
        logger.error('Invalid json response from api')
        sys.exit(1)

    groups = response['groups']
    if 'None' in groups:
        del groups['None']

    return groups


def _get_group_dna_file(group_name, asg_dna_files):
    group_name = slugify(rchop(group_name, '.json'))
    group_dna_file = None
    for asg_dna_file in asg_dna_files:
        if asg_dna_file == group_name:
            group_dna_file = asg_dna_file
            break

        group_name_json = group_name + '.json'
        if asg_dna_file == group_name_json:
            group_dna_file = asg_dna_file
            break

    if not group_dna_file:
        for asg_dna_file in asg_dna_files:
            if group_name.startswith(asg_dna_file):
                group_dna_file = asg_dna_file
                break

            stripped_asg_dna_file = asg_dna_file.replace('.json', '')
            if group_name.startswith(stripped_asg_dna_file):
                group_dna_file = asg_dna_file
                break

    if not group_dna_file:
        group_dna_file = group_name

    return group_dna_file


def dna_file_name_from_tags(args, dna_file_name, tags):
    env_tag = args['environment_tag']
    strip_env = args['strip_environment_from_dna_file_run_tag']
    tag = args['dna_file_tag']

    if not args['use_alternate_databag'] and args['dna_file_tag'] and tags.get(args['dna_file_tag'], None):
        dna_file_name = tags.get(tag, None)
        if strip_env and env_tag and tags.get(env_tag, None):
            environment = tags.get(env_tag, None)
            dna_file_name = strip_left(dna_file_name, environment)
            dna_file_name = strip_right(dna_file_name, environment)
            dna_file_name = dna_file_name.strip('_-')

    dna_file_name = rchop(dna_file_name, '.json') + '.json'
    return dna_file_name


def strip_right(text, suffix):
    if not text.endswith(suffix):
        return text
    return text[:len(text)-len(suffix)]


def strip_left(text, prefix):
    if not text.startswith(prefix):
        return text
    return text[len(prefix):]


def rsync_project_dry(args, logger=None, **kwargs):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    if args['dry_run']:
        logger.info("[RSYNC_PROJECT] From {0} to {1} with opts='{2}' excluding='{3}'".format(kwargs.get('local_dir'), kwargs.get('remote_dir'), kwargs.get('extra_opts'), kwargs.get('exclude')))  # noqa
    else:
        out = rsync_project(**kwargs)
        if out.return_code != 0:
            logger.info("[RSYNC_PROJECT] Failed command with status code {0}, please run `chef-solo-cup clean` against this node".format(out.return_code))  # noqa
            sys.exit(0)


def run_dry(cmd, args, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    if args['dry_run']:
        logger.info("[RUN] {0}".format(cmd))
    else:
        return run(cmd)


def sudo_dry(cmd, args, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    if args['dry_run']:
        logger.info("[SUDO] {0}".format(cmd))
    else:
        return sudo(cmd)


def add_line_if_not_present_dry(args, filename, line, run_f=run, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    cmd = "grep -q -e '{0}' {1} || echo '{0}' >> {1}".format(line, filename)
    if args['dry_run']:
        logger.info("[SUDO] {0}".format(cmd))
    else:
        run_f(cmd)


def filter_hosts(args, hosts, logger=None):
    rules = args['blacklist_rules'].get(args['command'])
    if not rules:
        return hosts

    excludes = []
    for rule in rules:
        if rule.startswith('/') and rule.endswith('/'):
            pattern = rule[1:-1]
            if not pattern:
                continue

            excludes.append(pattern)
        else:
            excludes.append(rule)

    excludes = map(lambda x: re.compile(x), excludes)
    new_hosts = {}

    for host, config in hosts.items():
        skip = map(lambda regex: regex.search(host), excludes)
        skip = reduce(lambda x, y: x or y, skip)
        if skip:
            continue
        new_hosts[host] = config

    return new_hosts


def slugify(text):
    if type(text) == unicode:
        text = unidecode.unidecode(text)
    text = text.strip()
    text = text.lower()
    text = re.sub(r'[^a-z0-9_-]+', '-', text)
    text = re.sub(r'-{2,}', '-', text)

    return text


def rchop(s, ending):
    if s.endswith(ending):
        return s[:-len(ending)]
    return s
