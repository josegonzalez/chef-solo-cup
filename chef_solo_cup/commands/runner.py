from __future__ import with_statement

import argparse
import collections
import logging
import multiprocessing
import random
import Queue
import signal
import sys
import time

from fabric.api import env
from fabric.exceptions import NetworkError

from chef_solo_cup.helpers import run_dry, sudo_dry
from chef_solo_cup.log import setup_custom_logger
from chef_solo_cup.commands.bootstrap import bootstrap
from chef_solo_cup.commands.clean import clean
from chef_solo_cup.commands.default import default
from chef_solo_cup.commands.gem import gem
from chef_solo_cup.commands.ruby import ruby
from chef_solo_cup.commands.sync import sync
from chef_solo_cup.commands.test import test
from chef_solo_cup.commands.update import update

COLORS = [31, 32, 33, 34, 35, 36, 37 ]


def list_commands():
    return {
      'default': default,
      'clean': clean,
      'gem': gem,
      'ruby': ruby,
      'run': run_command,
      'sudo': sudo_command,
      'sync': sync,
      'test': test,
      'update': update,
    }


def run_command(args, config, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    run_dry(args.cmd, args, logger=logger)


def sudo_command(args, config, logger=None):
    if logger is None:
        logger = setup_custom_logger('chef-solo-cup', args)

    sudo_dry(args.cmd, args, logger=logger)


def run_in_serial(args, hosts, logger=None):
    logger.info("Running commands in serial mode")
    commands = list_commands()

    for host in sorted(hosts.keys()):
        config = hosts[host]
        logger.info("Running {0} against {1}".format(args.command, host))

        _run_command(host, config, commands, args, logger)

def run_in_parallel(args, hosts, logger=None):
    logger.info("Running commands in parallel mode")
    commands = list_commands()

    task_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    for host in hosts.keys():
        task_queue.put({'host': host, 'config': hosts[host]})

    _colors = dict(red=31, green=32, yellow=33,
                   blue=34, magenta=35, cyan=36)

    workers = []
    pool_size = multiprocessing.cpu_count() * 2
    for worker_id in range(pool_size):
        color = _colors.pop(random.choice(_colors.keys()), None)
        tmp = multiprocessing.Process(target=_worker,
                                      args=(worker_id, task_queue, result_queue, commands, color, args, logger))
        tmp.start()
        workers.append(tmp)

    try:
        for worker in workers:
            worker.join()
    except KeyboardInterrupt:
        print "\x1b[0m"
        print 'parent received ctrl-c'
        for worker in workers:
            worker.terminate()
            worker.join()

    # while not result_queue.empty():
    #     pass  # return of each command can be accessed via result_queue.get(block=False)


def _worker(worker_id, task_queue, result_queue, commands, color, args, logger):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    logger = _update_handlers(logger, color, args)

    while not task_queue.empty():
        try:
            task = task_queue.get(block=False)
            logger.info("Running {0} against {1}".format(
                args.command,
                task['host']
            ))

            response = _run_command(task['host'], task['config'], commands, args, logger)
            result_queue.put(response)
        except Queue.Empty:
            pass

def _update_handlers(logger, color, args):
    has_args = args is not None and type(args) == argparse.Namespace
    is_debug = has_args and args.debug == True

    logger.handlers = []
    formatter = logging.Formatter('\x1b[{0};1m[{1}]\x1b[0m [%(asctime)s] %(levelname)-7s %(message)s'.format(color, multiprocessing.current_process().name))

    handler = logging.StreamHandler()
    if has_args and args.output is not None:
        handler = logging.FileHandler(output)

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    sys.stdout = StreamToLogger(logger, logging.INFO)
    sys.stderr = StreamToLogger(logger, logging.ERROR)
    return logger


def _run_command(host, config, commands, args, logger):
    env.use_ssh_config = True
    env.user = args.user

    if args.ip_address:
        env.host = args.ip_address
        env.host_string = args.ip_address
    else:
        env.host = host
        env.host_string = config.get('public_ip', host)

    if args.key_filename:
        env.key_filename = [args.key_filename, ]

    try:
        if args.command == 'bootstrap':
            env.abort_on_prompts = True
            bootstrap(args, config, logger=logger)
            update(args, config, logger=logger)
        elif args.command in commands:
            commands[args.command](args, config, logger=logger)
    except NetworkError as e:
        logger.exception("There was a network error: {0}".format(e.message))
        return False

    return True


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

    def isatty(self):
        return True
