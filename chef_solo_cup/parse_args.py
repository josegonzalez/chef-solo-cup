import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Chef-solo-cup, a chef-solo wrapper',
                                epilog="Chef Solo Cup is pwnage",
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', help='command to run', choices=['bootstrap', 'clean', 'default', 'gem', 'ruby', 'run', 'sync', 'sudo', 'test', 'update'])
    parser.add_argument('-c', '--command', help='command to run', dest='cmd', default=False)
    parser.add_argument('-d', '--dna_patterns', help='space-separated list of patterns to match against dna file names', default=None, dest='dna_patterns', nargs='+')
    parser.add_argument('-D', '--debug', help='enable debug mode', dest='debug', default=False, action='store_true')
    parser.add_argument('-k', '--key_filename', help='full path to key filename (pem key)', default=None, dest='key_filename')
    parser.add_argument('-l', '--loglevel', help='The chef log level to use', choices=['debug', 'info', 'warn', 'error', 'fatal'], dest='loglevel', default='info')
    parser.add_argument('-o', '--output', help='file to pipe output to (in addition to stdout)', default=None, dest='output')
    parser.add_argument('-p', '--providers', help='space-separated list of providers', dest='providers', nargs='*')
    parser.add_argument('-r', '--regions', help='space-separated list of regions', dest='regions', nargs='*')
    parser.add_argument('-R', '--repository', help='repository to use when cloning instead of using rsync', dest='repository')
    parser.add_argument('-s', '--services', help='space-separated list of services', dest='services', nargs='*')
    parser.add_argument('-S', '--sync', help='method to sync chef with', dest='sync', default='rsync', choices=['git', 'rsync'])
    parser.add_argument('-u', '--user', help='user to run commands as', dest='user', default='deploy')
    parser.add_argument('-v', '--version', help='Print version and exit', dest='version', default=False, action='store_true')

    parser.add_argument('--dry_run', help='perform a dry run of all commands', dest='dry_run', default=False, action='store_true')
    parser.add_argument('--chef_version', help='chef version to install', dest='chef_version', default='10.16.4')
    parser.add_argument('--ohai_version', help='ohai version to install', dest='ohai_version', default='6.14.0')
    parser.add_argument('--chef_file_dest', help='chef file destination on disk', dest='chef_file_dest', default='/tmp/chef')

    return parser.parse_args()
