from argparse import ArgumentParser
from os import path, mkdir, environ


# TODO add description

# TODO Add --socks and --hyper-text

# TODO FUTURE add --socks5-only, --socks4-only, --http-only, --https-only


class Config:
    @classmethod
    def __init__(cls):
        cls.verbose = False
        cls.timeout = 10
        cls.threads = 4
        cls.dont_shuffle = False

        cls.workdir = environ['HOME'] + '/proxies'
        if not path.isdir(cls.workdir):
            mkdir(cls.workdir)
        cls.list_file = 'proxylist.txt'
        cls.stats_file = 'proxy-stats.json'

    @classmethod
    def parse_args(cls):
        from utils import prl, colored, PRL_VERB, PRL_WARN

        args = Args.parse_arguments()

        if args.verbose:
            cls.verbose = args.verbose

        if args.timeout:
            cls.timeout = args.timeout
            prl('Timeout set to' + colored(cls.timeout, 'cyan'), PRL_VERB)

        if args.threads:
            cls.threads = args.threads
            prl('Using %s threads' % colored(cls.threads, 'cyan'), PRL_VERB)

        if args.no_shuffle:
            cls.dont_shuffle = args.no_shuffle
            prl("Won't shuffle list after loading", PRL_VERB)

        if args.workdir:
            if not path.isdir(args.workdir):
                prl('No such directory: ' + colored(args.workdir, 'cyan'), PRL_WARN)
            else:
                cls.workdir = args.workdir
                prl('Workdir is now: ' + colored(args.workdir, 'cyan'), PRL_VERB)

        if args.list_file:
            cls.list_file = args.list_file
            prl('List file is now: ' + colored(args.list_name, 'cyan'), PRL_VERB)

        if args.stats_file:
            cls.stats_file = args.stats_file
            prl('Stats file is now: ' + colored(args.stats_name, 'cyan'), PRL_VERB)


class Args:
    @classmethod
    def parse_arguments(cls):
        from utils import colored
        parser = ArgumentParser()

        parser.add_argument('-v', '--verbose', action='store_true',
                            help='Show verbose info')

        parser.add_argument('--timeout', metavar='[sec]', type=int,
                            help='How long should we wait for a response')

        parser.add_argument('--threads', type=int,
                            help='How many threads should we run (default: %s)' % colored(Config.threads, 'green'))

        parser.add_argument('--no-shuffle', action='store_true',
                            help="Don't shuffle proxy list after loading")

        parser.add_argument('--workdir', type=str,
                            help='The working directory of the script (default: %s)' % colored(Config.workdir, 'green'))

        parser.add_argument('--list-file', type=str,
                            help='The proxy-list file name (default: %s)' % colored(Config.list_file, 'green'))

        parser.add_argument('--stats-file', type=str,
                            help='The proxy-stats file name (default: %s)' % colored(Config.stats_file, 'green'))

        return parser.parse_args()
