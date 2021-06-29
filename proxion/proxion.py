from pathlib import Path
from random import choice
from threading import active_count
from time import sleep, time
from typing import Generator, Dict, List, Tuple
from site import USER_BASE

from .common import is_proxy_format, PROXY_TYPES
from .checker import CheckerThread, CheckResult
from .conf import Config
from .stats import update_stats

from termcolor import colored, cprint
from interutils import clear, pr

banner = Path(USER_BASE).joinpath(
    'proxion', 'assets', 'banner.txt').read_text()


def show_status(results: Tuple[List[CheckResult], List[str]]) -> None:
    ''' Show status (using the collected results) '''
    working, down = results[0], results[1]
    clear()
    cprint(banner, choice(('red', 'green', 'blue')))
    text = 'Working:'
    protocols = sort_protocols(working)
    for proto in protocols.keys():
        if len(protocols[proto]) > 0:
            text += f' {colored(proto.upper(), "blue")}:{colored(len(protocols[proto]), "green")}'
    pr(text)
    pr('Down: ' + colored(len(down), 'cyan'))
    pr('Total tried: ' + colored(len(working) + len(down), 'cyan'))
    print()


def sort_protocols(working: List[CheckResult]) -> Dict[str, list]:
    ''' Sort proxies by ProxyType'''
    x = {}
    for p in PROXY_TYPES:
        x.update({p: []})

    for i in working:
        x[i.proto].append(i)
    return x


def collect_results(threads: list):
    '''A helper to collect status of currently running threads'''

    working, down = [], []
    for i in range(Config.threads):
        working += threads[i].working
        down += threads[i].down
    return working, down


def load_list() -> (Generator[str, None, None], None):
    '''Load proxies from store specified in config'''

    pr('Loading proxies..', '*')
    list_file = Config.get_list_file()
    if not list_file.is_file():
        pr(f'No such file: {str(list_file)}', 'X')
        return

    for pip in list_file.read_text().splitlines():
        if not is_proxy_format(pip):
            pr(f'Bad proxy format: "{pip}", skipping!', '!')
            continue
        yield pip


def proxion():
    '''Main thread runner'''

    proxies_to_check = list(load_list())
    if not proxies_to_check:
        pr('Seems we are out of fresh proxies!', '!')
        return

    threads = []
    pr(f'Checking {colored(len(proxies_to_check), "green")} proxies on {colored(Config.threads, "cyan")} threads')
    for i in range(Config.threads):
        threads.append(CheckerThread(proxies_to_check))
        threads[i].setDaemon(True)
        threads[i].start()
        # sleep(0.1)
    try:
        while active_count() - 1:
            sleep(5)
            show_status(collect_results(threads))
        pr("All threads done.")
    except KeyboardInterrupt:
        print()
        pr('Interrupted!', '!')
    finally:
        pr('Saving checked..')
        update_stats(time(), collect_results(threads))
