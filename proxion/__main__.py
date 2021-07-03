#!/bin/env python3
import sys
from pathlib import Path
from typing import Iterable
from json import dumps

from interutils import pr, cyan

from proxion.util import (
    is_proxy_format,
    InvalidProxyFormatError,
    Proxy,
    parse_proxies_file,
    ProxyDB,
    print_banner,
)
from proxion import Config
from proxion.checker import ProxyChecker


def main() -> int:
    args = Config.init()
    if not args:
        return 1

    if not args.verbose:
        print_banner()

    if args.verbose:
        pr('Loading proxy DB.. ', '*', end='')
    ProxyDB(Config.get_db_file())
    if args.verbose:
        print('Done!')

    if Config.verbose:
        pr('Running with args:', '*')
        print(str(args))

    # Modify
    mode = args.mode.lower()
    if mode.startswith('a'):
        mod('add', args.proxies, args.submode)

    elif mode.startswith('r'):
        mod('remove', args.proxies, args.submode)

    # Query
    elif mode.startswith('q'):
        buffer = query(args.num, args.no_shuffle,
                       args.format, args.json_inline, args.info, args.proto)
        print(buffer)

    # Checker
    elif mode.startswith('c'):
        checker(args)


def mod(mode: str, proxies: Iterable[str], submode: str):
    def _mod_from_file(action: str, path: Path) -> int:
        '''
        Attempt to read file and for each line update/remove proxy in the DB.
        Catches exceptions.

        returns -> int: Count of proxies modified
        '''
        pr(f'{action}ing from a proxy list: {cyan(str(path))}')
        method = ProxyDB.update_some if action == 'Add' else ProxyDB.remove_some
        count = method(parse_proxies_file(path))
        if not count:
            return pr('No proxies added!', '!')
        pr(f'{action}ed {cyan(count)} proxies!')
        return count

    def _mod_single_proxy(action: str, proxy_ip: str) -> bool:
        '''
        Attempt to update/remove single proxy in the DB.
        Catches exceptions.

        returns -> bool: Success
        '''
        pr(f'{action}ing a single proxy: {cyan(proxy_ip)}')
        method = ProxyDB.update_one if action == 'Add' else ProxyDB.remove_one
        try:
            method(Proxy(proxy_ip))
            return True
        except KeyError:
            pr(f'Proxy {cyan(str(proxy_ip))} not found in DB!', '!')
        except InvalidProxyFormatError:
            pr(f'Invalid proxy format: {cyan(str(proxy_ip))}', '!')
        return False

    action = 'Add' if mode == 'add' else 'Remov'
    for arg in proxies:
        try:
            if not submode:
                arg_path = Path(arg)
                if arg_path.is_file():
                    _mod_from_file(action, arg_path)
                elif is_proxy_format(arg):
                    _mod_single_proxy(action, arg)
                else:
                    raise ValueError

            elif submode == 'literal':
                if not is_proxy_format(arg):
                    raise ValueError
                _mod_single_proxy(action, arg)

            elif submode == 'file':
                if not Path(arg).is_file():
                    raise ValueError
                _mod_from_file(action, arg)
        except ValueError:
            pr(f'Invalid argument: {cyan(arg)}', '!')


def query(num: int = 0,
          no_shuffle: bool = False,
          fmt: str = 'json',
          json_inline: bool = False,
          info: bool = True,
          proto: Iterable = tuple()) -> Iterable[Proxy]:

    if fmt == 'json':
        buffer = []
    if fmt == 'grep':
        buffer = ''
    count = 0
    for proxy in ProxyDB.get_proxies(not no_shuffle):
        if fmt == 'json':
            if not info:
                buffer.append(proxy.pip)
            else:
                buffer.append(proxy.serialize())
        elif fmt == 'grep':
            buffer += proxy.pip
            if info:
                for key, val in proxy.serialize()[proxy.pip].items():
                    buffer += f' ,{key}:{val}'
            buffer += '\n'
        count += 1
        if count == num:
            break

    if fmt == 'json':
        _indent = 4
        if json_inline:
            _indent = None
        buffer = dumps(buffer, indent=_indent)
    return buffer


def checker(args):
    if args.verbose:
        pr(f'Timeout set to {cyan(args.timeout)} sec', '*')
        pr(f'Using max {cyan(args.max_threads)} threads', '*')
        pr(f'Shuffling proxies: {cyan(not args.no_shuffle)}', '*')
        pr(f'Checking only for the following protocols: {cyan(", ".join(args.protocols))}', '*')

    # Gather proxies to check
    checklist = []
    if args.literal:
        pr('Checking proxies from CLI arguments')
        for arg in args.literal:
            if not is_proxy_format(arg):
                raise ValueError
            checklist.append(Proxy(arg))
    elif args.file:
        pr('Checking proxies from CLI argument files')
        for arg in args.file:
            path = Path(arg)
            if not path.is_file():
                raise ValueError
            checklist += [Proxy(p) for p in parse_proxies_file(path)]
    else:
        pr('Checking proxies from the ProxyDB')
        checklist = ProxyDB.get_proxies()

    ProxyChecker(checklist, args.max_threads, args.protocols,
                 args.timeout, args.no_shuffle, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
