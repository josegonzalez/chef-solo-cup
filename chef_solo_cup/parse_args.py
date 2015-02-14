# -*- coding: utf-8 -*-

import argparse
import json
import os
import re


def parse_args():
    defaults = {
        "api-password": None,
        "api-url": None,
        "api-username": None,
        "asg-dna-path": "dna/asg",
        "aws-access-key-id": None,
        "aws-secret-access-key": None,
        "command": False,
        "config-path": "solo-config.rb",
        "dna-patterns": None,
        "debug": False,
        "exclude": None,
        "rsync-exclusions": None,
        "ip-address": None,
        "key-filename": None,
        "loglevel": "info",
        "log-path": None,
        "output": None,
        "parallel": False,
        "providers": None,
        "quantity": None,
        "regions": None,
        "repository": None,
        "services": None,
        "sync": "rsync",
        "user": "deploy",
        "dry-run": False,
        "chef-version": "10.16.4",
        "ohai-version": "6.14.0",
        "chef-file-dest": "/tmp/chef",
    }

    cwd = os.path.realpath(os.getcwd())
    paths = [
        os.path.join(cwd, 'chef-solo-cup.json'),
        os.path.join(cwd, '.chef', 'chef-solo-cup.json'),
        os.path.join(cwd, '.chef', 'config.json'),
        os.path.join(cwd, '.chef', 'user-config.json'),
    ]

    # Regular expression for comments
    comment_re = re.compile(
        '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
        re.DOTALL | re.MULTILINE
    )

    def parse_json(filename):
        """
        From: http://www.lifl.fr/~riquetd/parse-a-json-file-with-comments.html
        """
        with open(filename) as f:
            content = ''.join(f.readlines())
            match = comment_re.search(content)
            while match:
                content = content[:match.start()] + content[match.end():]
                match = comment_re.search(content)
            return json.loads(content)

    config = {}
    for path in paths:
        try:
            data = parse_json(path)
            config = dict(config.items() + data.items())
            break
        except IOError:
            pass

    options = dict(defaults.items() + config.items())

    parser = argparse.ArgumentParser(
        description='Chef-solo-cup, a chef-solo wrapper',
        epilog="Chef Solo Cup is pwnage",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'command',
        choices=[
            'bootstrap',
            'clean',
            'default',
            'gem',
            'inspect',
            'ruby',
            'run',
            'sync',
            'sudo',
            'test',
            'update',
        ],
        help='command to run',
        nargs='?'
    )
    parser.add_argument(
        '-a',
        '--asg-dna-path',
        default=options['asg-dna-path'],
        dest='asg_dna_path',
        help='Path to asg dna files (relative to repo base)'
    )
    parser.add_argument(
        '-c',
        '--command',
        default=options['command'],
        dest='cmd',
        help='command to run'
    )
    parser.add_argument(
        '-C',
        '--config-path',
        default=options['config-path'],
        dest='config_path',
        help='relative path from chef file destination to solo config file'
    )
    parser.add_argument(
        '-d',
        '--dna-patterns',
        default=options['dna-patterns'],
        dest='dna_patterns',
        help='space-separated list of patterns to match against dna filenames',
        nargs='+'
    )
    parser.add_argument(
        '-D',
        '--debug',
        action='store_true',
        default=options['debug'],
        dest='debug',
        help='enable debug mode'
    )
    parser.add_argument(
        '-e',
        '--exclude',
        help='A regex to exclude hosts by',
        default=options['exclude'],
        dest='exclude',
        nargs='+'
    )
    parser.add_argument(
        '-E',
        '--rsync-exclusions',
        default=options['rsync-exclusions'],
        dest='rsync_exclusions',
        help='space-separated list of files to exclude in rsync',
        nargs='+'
    )
    parser.add_argument(
        '-i',
        '--ip-address',
        default=options['ip-address'],
        dest='ip_address',
        help='The ip address to connect to'
    )
    parser.add_argument(
        '-k',
        '--key-filename',
        default=options['key-filename'],
        dest='key_filename',
        help='full path to key filename (pem key)'
    )
    parser.add_argument(
        '-l',
        '--loglevel',
        choices=['debug', 'info', 'warn', 'error', 'fatal'],
        default=options['loglevel'],
        dest='loglevel',
        help='The chef log level to use',
    )
    parser.add_argument(
        '-L',
        '--log-path',
        default=options['log-path'],
        dest='log_path',
        help='The path to write logs to'
    )
    parser.add_argument(
        '-o',
        '--output',
        default=options['output'],
        dest='output',
        help='file to pipe output to (in addition to stdout)'
    )
    parser.add_argument(
        '-P',
        '--parallel',
        action='store_true',
        default=options['parallel'],
        dest='parallel',
        help='whether to run commands in parallel'
    )
    parser.add_argument(
        '-p',
        '--providers',
        default=options['providers'],
        dest='providers',
        help='space-separated list of providers',
        nargs='*'
    )
    parser.add_argument(
        '-q',
        '--quantity',
        default=options['quantity'],
        dest='quantity',
        help='The number of nodes to provision'
    )
    parser.add_argument(
        '-r',
        '--regions',
        default=options['regions'],
        dest='regions',
        help='space-separated list of regions',
        nargs='*'
    )
    parser.add_argument(
        '-R',
        '--repository',
        default=options['repository'],
        dest='repository',
        help='repository to use when cloning instead of using rsync'
    )
    parser.add_argument(
        '-s',
        '--services',
        default=options['services'],
        dest='services',
        help='space-separated list of services',
        nargs='*'
    )
    parser.add_argument(
        '-S',
        '--sync',
        choices=['git', 'rsync'],
        default=options['sync'],
        dest='sync',
        help='method to sync chef with'
    )
    parser.add_argument(
        '-u',
        '--user',
        default=options['user'],
        dest='user',
        help='user to run commands as'
    )
    parser.add_argument(
        '-v',
        '--version',
        action='store_true',
        dest='version',
        default=False,
        help='Print version and exit'
    )

    parser.add_argument(
        '--api-password',
        default=options['api-password'],
        dest='api_password',
        help='basic auth password for api'
    )
    parser.add_argument(
        '--api-url',
        default=options['api-url'],
        dest='api_url',
        help='backing url for api'
    )
    parser.add_argument(
        '--api-username',
        default=options['api-username'],
        dest='api_username',
        help='basic auth username for api'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=options['dry-run'],
        dest='dry_run',
        help='perform a dry run of all commands'
    )
    parser.add_argument(
        '--chef-version',
        default=options['chef-version'],
        dest='chef_version',
        help='chef version to install'
    )
    parser.add_argument(
        '--ohai-version',
        default=options['ohai-version'],
        dest='ohai_version',
        help='ohai version to install'
    )
    parser.add_argument(
        '--chef-file-dest',
        default=options['chef-file-dest'],
        dest='chef_file_dest',
        help='chef file destination on disk'
    )

    # AWS
    parser.add_argument(
        '--aws-access-key-id',
        default=options['aws-access-key-id'],
        dest='aws_access_key_id',
        help='AWS Access Key'
    )
    parser.add_argument(
        '--aws-secret-access-key',
        default=options['aws-secret-access-key'],
        dest='aws_secret_access_key',
        help='AWS Secret Key'
    )

    return vars(parser.parse_args())
