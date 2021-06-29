from argparse import ArgumentParser, _ArgumentGroup
from pathlib import Path

from .common import is_proxy_format

from termcolor import colored
from interutils import pr, cyan, choose, DictConfig


class Config:
    @classmethod
    def init(cls) -> int:
        # General
        cls.verbose = False

        # Checker
        cls.timeout = 10
        cls.threads = 4
        cls.dont_shuffle = False

        # Workspace
        cls.store = Path().home().joinpath('.cache', 'proxion')
        cls.store.mkdir(exist_ok=True)

        cls.list_file = 'proxylist.txt'
        cls.stats_file = 'proxy-stats.json'

        # Proto
        cls.protocols = ()

        # Parse arguments
        return cls.parse_args()

    @classmethod
    def get_stats_file(cls) -> Path:
        return cls.store.joinpath(cls.stats_file)

    @classmethod
    def get_list_file(cls) -> Path:
        return cls.store.joinpath(cls.list_file)

    @classmethod
    def parse_args(cls) -> int:
        args = Args.parse_arguments()

        # General
        if args.verbose:
            cls.verbose = args.verbose
        if args.store:
            try:
                args.store = Path(args.store)
                if not args.store.isdir():
                    raise FileNotFoundError
            except:
                pr(f'No such directory: {colored(str(args.store), "cyan")} , using default!', '!')
            else:
                cls.store = args.store
                pr('Store directory is now: ' +
                   colored(str(args.store), 'cyan'), '*')
        if args.list_file:
            cls.list_file = args.list_file
            pr('List file is now: ' + colored(args.list_name, 'cyan'), '*')
        if args.stats_file:
            cls.stats_file = args.stats_file
            pr('Stats file is now: ' + colored(args.stats_name, 'cyan'), '*')

        # Database
        if args.add:
            cls.db_mode = 'add'
            modify_path = Path(args.add)
            if modify_path.is_file():
                pr(f'Adding a proxy list: {cyan(str(modify_path))}')
                cls.modify_path = modify_path
            else:
                if is_proxy_format(args.add):
                    pr(f'Adding a single proxy: {cyan(args.add)}')
                    cls.modify_proxy = args.add
                pr('No such file!', 'X')
                return 1

        elif args.remove:
            cls.db_mode = 'remove'
            modify_path = Path(args.remove)
            if modify_path.is_file():
                pr(f'Removing a proxy list: {cyan(str(modify_path))}')
                cls.modify_path = modify_path
            else:
                if is_proxy_format(args.remove):
                    pr(f'Removing a single proxy: {cyan(args.remove)}')
                    cls.modify_proxy = args.remove
                pr('No such file!', 'X')
                return 1

        elif args.clear_db:
            c = choose(
                prompt='Are you sure you wish to clear whole database?', default=1)
            if c != 0:
                return 0
            elif c == 1:
                # Clear database
                # TODO
                pass

        # Checker
        if args.timeout:
            cls.timeout = args.timeout
            pr('Timeout set to' + colored(cls.timeout, 'cyan'), '*')
        if args.threads:
            cls.threads = args.threads
            pr(f'Using {colored(cls.threads, "cyan")} threads', '*')
        if args.no_shuffle:
            cls.dont_shuffle = args.no_shuffle
            pr("Won't shuffle list after loading", '*')
        # Checker - Protocols
        if args.socks:
            cls.protocols = ('socks5', 'socks4')
            pr(f'Checking only {colored("SOCKS5", "blue")} and {colored("SOCKS4", "blue")}')
        elif args.hyper:
            cls.protocols = ('https', 'http')
            pr(f'Checking only {colored("HTTP", "blue")} and {colored("HTTPS", "blue")}')
        elif args.socks5_only:
            cls.protocols = ('socks5',)
            pr(f'Checking only {colored("SOCKS5", "blue")}')
        elif args.socks4_only:
            cls.protocols = ('socks4',)
            pr(f'Checking only {colored("SOCKS4", "blue")}')
        elif args.https_only:
            cls.protocols = ('https',)
            pr(f'Checking only {colored("HTTPS", "blue")}')
        elif args.http_only:
            cls.protocols = ('http',)
            pr(f'Checking only {colored("HTTP", "blue")}')
        else:
            cls.protocols = ('socks5', 'socks4', 'https', 'http')


class Args:
    @classmethod
    def parse_arguments(cls):
        parser = ArgumentParser()
        cls.general_args(parser.add_argument_group(
            colored('~=~ GENERAL ~=~', 'green')))
        cls.database_args(parser.add_argument_group(
            colored('~=~ DATABASE ~=~', 'green')))
        cls.checker_args(parser.add_argument_group(
            colored('~=~ CHECKER ~=~', 'green')))
        return parser.parse_args()

    @classmethod
    def general_args(cls, args: _ArgumentGroup):
        args.add_argument('-v', '--verbose', action='store_true',
                          help='Show verbose info')
        args.add_argument('--store', type=str,
                          help=f'The storage directory of the script (default: {colored(Config.store, "green")})')
        args.add_argument('--list-file', type=str,
                          help=f'The proxy-list file name (default: {colored(Config.list_file, "green")})')
        args.add_argument('--stats-file', type=str,
                          help=f'The proxy-stats file name (default: {colored(Config.stats_file, "green")})')

    @classmethod
    def database_args(cls, args: _ArgumentGroup):
        args.add_argument('-a', '--add', type=str,
                          help="Path to a proxy list to add into the database")
        args.add_argument('-r', '--remove', type=str,
                          help="Either a proxy IP:PORT or path to a list of proxies to remove from the database")
        args.add_argument('--clear-db', action='store_true',
                          help="Empty the database")

    @classmethod
    def checker_args(cls, args: _ArgumentGroup):
        args = args.add_mutually_exclusive_group()

        args.add_argument('--timeout', metavar='[sec]', type=int,
                          help=f'How long to wait for a response (default: {colored(Config.timeout, "green")})')
        args.add_argument('--threads', type=int,
                          help=f'How many threads should we run (default: {colored(Config.threads, "green")})')
        args.add_argument('--no-shuffle', action='store_true',
                          help="Don't shuffle proxy list after loading")

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
