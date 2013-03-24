import argparse
import json
import os


def parse_args():
    defaults = {
        "command": False,
        "config-path": "solo-config.rb",
        "dna-patterns": None,
        "debug": False,
        "exclude": None,
        "ip-address": None,
        "key-filename": None,
        "loglevel": "info",
        "output": None,
        "providers": None,
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

    try:
        config_path = os.environ.get('CUP_CONFIG_PATH', os.path.realpath(os.getcwd()), 'chef-solo-cup.json')
        config_file = os.path.join(config_path)
        with open(config_file) as f:
            config = json.loads(f.read())
    except IOError:
        config = {}

    options = dict(defaults.items() + config.items())

    parser = argparse.ArgumentParser(description='Chef-solo-cup, a chef-solo wrapper',
                                     epilog="Chef Solo Cup is pwnage",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', help='command to run', choices=['bootstrap', 'clean', 'default', 'gem', 'ruby', 'run', 'sync', 'sudo', 'test', 'update'])
    parser.add_argument('-c', '--command', help='command to run', default=options['command'], dest='cmd')
    parser.add_argument('-C', '--config-path', help='relative path from chef file destination to solo config file', default=options['config-path'], dest='config_path')
    parser.add_argument('-d', '--dna-patterns', help='space-separated list of patterns to match against dna file names', default=options['dna-patterns'], dest='dna_patterns', nargs='+')
    parser.add_argument('-D', '--debug', help='enable debug mode', default=options['debug'], dest='debug', action='store_true')
    parser.add_argument('-e', '--exclude', help='A regex to exclude hosts by', default=options['exclude'], dest='exclude', nargs='+')
    parser.add_argument('-i', '--ip-address', help='The ip address to connect to', default=options['ip-address'], dest='ip_address')
    parser.add_argument('-k', '--key-filename', help='full path to key filename (pem key)', default=options['key-filename'], dest='key_filename')
    parser.add_argument('-l', '--loglevel', help='The chef log level to use', default=options['loglevel'], dest='loglevel', choices=['debug', 'info', 'warn', 'error', 'fatal'])
    parser.add_argument('-o', '--output', help='file to pipe output to (in addition to stdout)', default=options['output'], dest='output')
    parser.add_argument('-p', '--providers', help='space-separated list of providers', default=options['providers'], dest='providers', nargs='*')
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

    return parser.parse_args()
