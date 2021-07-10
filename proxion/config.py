from argparse import ArgumentParser
from pathlib import Path
from multiprocessing import cpu_count
from typing import Set

from termcolor import colored
from interutils import pr, cyan


class Defaults:
    store = Path().home().joinpath('.cache', 'proxion')
    db_file = 'proxydb.json'
    checker_max_threads = cpu_count() - 1
    checker_proxy_protocols: Set[str] = set(
        {'socks5', 'socks4', 'https', 'http'})
    checker_timeout = 10


class Config:

    @classmethod
    def init(cls) -> int:
        args = Args.parse_arguments()

        # General
        cls.verbose = args.verbose

        # Workspace
        cls.store = Defaults.store
        if args.store:
            try:
                args.store = Path(args.store)
                if not args.store.isdir():
                    raise FileNotFoundError
            except FileNotFoundError:
                pr(f'No such directory: {colored(str(args.store), "cyan")} , using default!', '!')
            else:
                cls.store = args.store
        cls.store.mkdir(exist_ok=True)

        cls.db_file = args.db_file

        if cls.verbose:
            pr(f'Using store directory in: {cyan(str(cls.store))}', '*')
            pr(f'Using proxies DB named: {cyan(cls.db_file)}', '*')

        return args

    @classmethod
    def get_db_file(cls) -> Path:
        return cls.store.joinpath(cls.db_file)


class Args:
    @classmethod
    def parse_arguments(cls):
        parser = ArgumentParser()

        subparser = parser.add_subparsers(
            title='The modes to run', dest='mode', required=True)
        cls.mode_modify(subparser.add_parser(
            'add', aliases=('a', 'A'), help='Add proxies to the database'))
        cls.mode_modify(subparser.add_parser(
            'remove', aliases=('r', 'R'), help='Remove proxies from the database'))
        cls.mode_query(subparser.add_parser(
            'query', aliases=('q', 'Q'), help='Query the database for proxies'))
        cls.mode_check(subparser.add_parser(
            'check', aliases=('c', 'C'), help='Check proxies'))

        parser.add_argument('-v', '--verbose', action='store_true',
                            help='Show verbose info')
        parser.add_argument('--store', type=str,
                            help=f'The storage directory of the script (default: \
                                {colored(Defaults.store, "green")})')
        parser.add_argument('--db-file', type=str, default=Defaults.db_file,
                            help=f'The proxy-db file name (default: \
                                {colored(Defaults.db_file, "green")})')

        return parser.parse_args()

    @classmethod
    def mode_modify(cls, args: ArgumentParser):
        args.add_argument(
            'proxies', nargs='+',
            help='Either literal proxy(ies) or file(s) containing proxies line-by-line')

        sub_mode = args.add_mutually_exclusive_group()
        sub_mode.add_argument('-l', '--literal', action='store_const',
                              const='literal', dest='submode',
                              help='Pass as argument (one or more) proxies')
        sub_mode.add_argument('-f', '--file', action='store_const',
                              const='file', dest='submode',
                              help='Pass as argument (one or more) files containing proxies')

    @classmethod
    def mode_query(cls, args: ArgumentParser):
        args.add_argument('-n', '--num', type=int, default=0,
                          help=f'Number of proxies to query (default: {cyan("all")})')
        args.add_argument('-ns', '--no-shuffle', action='store_true',
                          help="Don't shuffle array")
        args.add_argument('-f', '--format', type=str, choices=('json', 'grep'), default='json',
                          help=f'Format to return (default: {cyan("json")})')
        args.add_argument('--json-inline', action='store_true',
                          help='Print JSON format as a one-liner')
        args.add_argument('-ni', '--no-info', action='store_false', dest='info',
                          help="Don't add proxy info")
        args.add_argument('-p', '--protocols',
                          choices=Defaults.checker_proxy_protocols,
                          type=str, nargs="+", help=f'Proxies protocols to get (default: {cyan("all")})')

    @classmethod
    def mode_check(cls, args: ArgumentParser):
        args.add_argument('-t', '--timeout', metavar='[sec]',
                          type=int, default=Defaults.checker_timeout,
                          help=f'How long to wait for a response (default: \
                              {colored(Defaults.checker_timeout, "green")})')
        args.add_argument('-m', '--max-threads',
                          type=int, default=Defaults.checker_max_threads,
                          help=f'How many threads should we run (default: \
                              {colored(Defaults.checker_max_threads, "green")})')
        args.add_argument('-ns', '--no-shuffle', action='store_true',
                          help="Don't shuffle proxy list after loading")
        args.add_argument('-p', '--protocols', type=str, nargs='+',
                          choices=Defaults.checker_proxy_protocols,
                          help=f'Specify which protocols to check for (default: {cyan("all")})')
        args.add_argument('-ol', '--older', type=str,
                          help='Filter proxies by last checked time, use time suffix ' +
                          '[s, m, h, d, w, mo, y] (e.g. 10s, 20d, 3mo, 1y)')
        args.add_argument('-la', '--latency', type=int,
                          help='Filter proxies by latency [value should be preffixed with either + or - ' +
                          'while the plus meaning values higher than and the minus meaning ' +
                          'values lower than] (e.g. -90 , +150 )')
        args.add_argument('-ec', '--exit-country', type=str, nargs='+',
                          help='Filter proxies by exit country')
        args.add_argument('-s', '--strict', action='store_true',
                          help="When filtering don't include proxies without a value," +
                          " only filter proxies that strictly have a value")
        sub_mode = args.add_mutually_exclusive_group()
        sub_mode.add_argument('-l', '--literal', type=str, nargs='+',
                              help='Pass as argument (one or more) proxies')
        sub_mode.add_argument('-f', '--file', type=str, nargs='+',
                              help='Pass as argument (one or more) files containing proxies')
