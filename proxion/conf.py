from argparse import ArgumentParser
from os import path, mkdir, environ

from termcolor import colored
from interutils import pr


class Config:
    @classmethod
    def __init__(cls):
        # General
        cls.verbose = False
        cls.timeout = 10
        cls.threads = 4
        cls.dont_shuffle = False

        # Workspace
        cls.workdir = environ['HOME'] + '/proxies'
        if not path.isdir(cls.workdir):
            mkdir(cls.workdir)
        cls.list_file = 'proxylist.txt'
        cls.stats_file = 'proxy-stats.json'

        # Proto
        cls.protocols = None

    @classmethod
    def parse_args(cls):
        args = Args.parse_arguments()

        # General
        if args.verbose:
            cls.verbose = args.verbose
        if args.timeout:
            cls.timeout = args.timeout
            pr('Timeout set to' + colored(cls.timeout, 'cyan'), '*')
        if args.threads:
            cls.threads = args.threads
            pr('Using %s threads' % colored(cls.threads, 'cyan'), '*')
        if args.no_shuffle:
            cls.dont_shuffle = args.no_shuffle
            pr("Won't shuffle list after loading", '*')

        # Workspace
        if args.workdir:
            if not path.isdir(args.workdir):
                pr('No such directory: ' + colored(args.workdir, 'cyan'), '!')
            else:
                cls.workdir = args.workdir
                pr('Workdir is now: ' + colored(args.workdir, 'cyan'), '*')
        if args.list_file:
            cls.list_file = args.list_file
            pr('List file is now: ' + colored(args.list_name, 'cyan'), '*')
        if args.stats_file:
            cls.stats_file = args.stats_file
            pr('Stats file is now: ' + colored(args.stats_name, 'cyan'), '*')

        # Protocols
        if args.socks:
            cls.protocols = ('socks5', 'socks4')
            pr('Checking only %s and %s' % (colored('SOCKS5', 'blue'), colored('SOCKS4', 'blue')))
        elif args.hyper:
            cls.protocols = ('https', 'http')
            pr('Checking only %s and %s' % (colored('HTTP', 'blue'), colored('HTTPS', 'blue')))
        elif args.socks5_only:
            cls.protocols = tuple('socks5')
            pr('Checking only %s' % colored('SOCKS5', 'blue'))
        elif args.socks4_only:
            cls.protocols = tuple('socks4')
            pr('Checking only %s' % colored('SOCKS4', 'blue'))
        elif args.https_only:
            cls.protocols = tuple('https')
            pr('Checking only %s' % colored('HTTPS', 'blue'))
        elif args.http_only:
            cls.protocols = tuple('http')
            pr('Checking only %s' % colored('HTTP', 'blue'))
        else:
            cls.protocols = ('socks5', 'socks4', 'https', 'http')


class Args:
    @classmethod
    def parse_arguments(cls):
        parser = ArgumentParser()
        cls.general_args(parser.add_argument_group(colored('~=~ GENERAL ~=~', 'green')))
        cls.workspace_args(parser.add_argument_group(colored('~=~ WORKSPACE ~=~', 'green')))
        cls.proto_args(parser.add_argument_group(colored('~=~ PROTOCOLS ~=~', 'green')))
        return parser.parse_args()

    @classmethod
    def general_args(cls, args):
        args.add_argument('-v', '--verbose', action='store_true',
                          help='Show verbose info')
        args.add_argument('--timeout', metavar='[sec]', type=int,
                          help='How long to wait for a response (default: %s)' % colored(Config.timeout, 'green'))
        args.add_argument('--threads', type=int,
                          help='How many threads should we run (default: %s)' % colored(Config.threads, 'green'))
        args.add_argument('--no-shuffle', action='store_true',
                          help="Don't shuffle proxy list after loading")

    @classmethod
    def workspace_args(cls, args):
        args.add_argument('--workdir', type=str,
                          help='The working directory of the script (default: %s)' % colored(Config.workdir, 'green'))
        args.add_argument('--list-file', type=str,
                          help='The proxy-list file name (default: %s)' % colored(Config.list_file, 'green'))
        args.add_argument('--stats-file', type=str,
                          help='The proxy-stats file name (default: %s)' % colored(Config.stats_file, 'green'))

    @classmethod
    def proto_args(cls, args):
        args = args.add_mutually_exclusive_group()

        args.add_argument('--socks', action='store_true',
                          help='Only check SOCKS4 & SOCKS5 protocols')
        args.add_argument('--hyper', action='store_true',
                          help='Only check HTTP & HTTPS protocols')

        args.add_argument('--http-only', action='store_true',
                          help='Only check HTTP protocols')
        args.add_argument('--https-only', action='store_true',
                          help='Only check HTTPS protocol')
        args.add_argument('--socks4-only', action='store_true',
                          help='Only check SOCKS4 protocol')
        args.add_argument('--socks5-only', action='store_true',
                          help='Only check SOCKS5 protocol')
