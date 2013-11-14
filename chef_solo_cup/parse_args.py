import argparse
import json
import os
import re


def parse_args():
    defaults = {
        "asg-dna-path": "dna/asg",
        "aws-access-key-id": None,
        "aws-secret-access-key": None,
        "command": False,
        "config-path": "solo-config.rb",
        "dna-patterns": None,
        "debug": False,
        "exclude": None,
        "ip-address": None,
        "key-filename": None,
        "loglevel": "info",
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

    paths = [
        os.path.join(os.path.realpath(os.getcwd()), 'chef-solo-cup.json'),
        os.path.join(os.path.realpath(os.getcwd()), '.chef', 'chef-solo-cup.json'),
        os.path.join(os.path.realpath(os.getcwd()), '.chef', 'config.json'),
        os.path.join(os.path.realpath(os.getcwd()), '.chef', 'user-config.json'),
    ]

    # Regular expression for comments
    comment_re = re.compile(
        '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
        re.DOTALL | re.MULTILINE
    )

    def parse_json(filename):
        """From: http://www.lifl.fr/~riquetd/parse-a-json-file-with-comments.html"""
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

    parser = argparse.ArgumentParser(description='Chef-solo-cup, a chef-solo wrapper',
                                     epilog="Chef Solo Cup is pwnage",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', help='command to run', choices=['bootstrap', 'clean', 'default', 'gem', 'ruby', 'run', 'sync', 'sudo', 'test', 'update'], nargs='?')
    parser.add_argument('-a', '--asg-dna-path', help='Path to asg dna files (relative to repo base)', default=options['asg-dna-path'], dest='asg_dna_path')
    parser.add_argument('-c', '--command', help='command to run', default=options['command'], dest='cmd')
    parser.add_argument('-C', '--config-path', help='relative path from chef file destination to solo config file', default=options['config-path'], dest='config_path')
    parser.add_argument('-d', '--dna-patterns', help='space-separated list of patterns to match against dna file names', default=options['dna-patterns'], dest='dna_patterns', nargs='+')
    parser.add_argument('-D', '--debug', help='enable debug mode', default=options['debug'], dest='debug', action='store_true')
    parser.add_argument('-e', '--exclude', help='A regex to exclude hosts by', default=options['exclude'], dest='exclude', nargs='+')
    parser.add_argument('-i', '--ip-address', help='The ip address to connect to', default=options['ip-address'], dest='ip_address')
    parser.add_argument('-k', '--key-filename', help='full path to key filename (pem key)', default=options['key-filename'], dest='key_filename')
    parser.add_argument('-l', '--loglevel', help='The chef log level to use', default=options['loglevel'], dest='loglevel', choices=['debug', 'info', 'warn', 'error', 'fatal'])
    parser.add_argument('-o', '--output', help='file to pipe output to (in addition to stdout)', default=options['output'], dest='output')
    parser.add_argument('-P', '--parallel', help='whether to run commands in parallel', default=options['parallel'], dest='parallel', action='store_true')
    parser.add_argument('-p', '--providers', help='space-separated list of providers', default=options['providers'], dest='providers', nargs='*')
    parser.add_argument('-q', '--quantity', help='The number of nodes to provision', default=options['quantity'], dest='quantity')
    parser.add_argument('-r', '--regions', help='space-separated list of regions', default=options['regions'], dest='regions', nargs='*')
    parser.add_argument('-R', '--repository', help='repository to use when cloning instead of using rsync', default=options['repository'], dest='repository')
    parser.add_argument('-s', '--services', help='space-separated list of services', default=options['services'], dest='services', nargs='*')
    parser.add_argument('-S', '--sync', help='method to sync chef with', default=options['sync'], dest='sync', choices=['git', 'rsync'])
    parser.add_argument('-u', '--user', help='user to run commands as', default=options['user'], dest='user')
    parser.add_argument('-v', '--version', help='Print version and exit', dest='version', default=False, action='store_true')

    parser.add_argument('--dry-run', help='perform a dry run of all commands', default=options['dry-run'], dest='dry_run', action='store_true')
    parser.add_argument('--chef-version', help='chef version to install', default=options['chef-version'], dest='chef_version')
    parser.add_argument('--ohai-version', help='ohai version to install', default=options['ohai-version'], dest='ohai_version')
    parser.add_argument('--chef-file-dest', help='chef file destination on disk', default=options['chef-file-dest'], dest='chef_file_dest')

    # AWS

    parser.add_argument('--aws-access-key-id', help='AWS Access Key', default=options['aws-access-key-id'], dest='aws_access_key_id')
    parser.add_argument('--aws-secret-access-key', help='AWS Secret Key', default=options['aws-secret-access-key'], dest='aws_secret_access_key')

    return parser.parse_args()
