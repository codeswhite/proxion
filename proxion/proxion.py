from os.path import join, isfile
from random import choice
from threading import active_count
from time import sleep, time
from typing import Generator, Dict, List, Tuple
from ipaddress import AddressValueError, IPv4Address

from .checker import CheckerThread, CheckResult
from .conf import Config
from .stats import update_stats

from termcolor import colored, cprint
from interutils import clear, pr

banner = """
    ____                  _                      
   / __ \_________  _  __(_)___  ____  
  / /_/ / ___/ __ \| |/_/ / __ \/ __ \ 
 / ____/ /  / /_/ />  </ / /_/ / / / / 
/_/   /_/   \____/_/|_/_/\____/_/ /_/  
"""

PROXY_TYPES = ('socks5', 'socks4', 'https', 'http')


def _check_proxy_format(proxy) -> bool:
    # Check that the given proxy is a string and has a valid address + port

    def is_ip_address(ip: str) -> bool:
        try:
            IPv4Address(ip)
            return True
        except AddressValueError:
            return False

    if type(proxy) is not str:
        return False
    x = proxy.strip().split(':')
    if len(x) != 2:
        return False
    ip, port = x
    try:
        port = int(port)
    except ValueError:
        return False
    if port < 0 or port > 65535:
        return False
    if not is_ip_address(ip):
        return False
    return True


def show_status(results: Tuple[List[CheckResult], List[str]]) -> None:
    working, down = results[0], results[1]
    clear()
    cprint(banner, choice(('red', 'green', 'blue')))
    text = 'Working:'
    protocols = sort_protocols(working)
    for proto in protocols.keys():
        if len(protocols[proto]) > 0:
            text += ' %s:%s' % (colored(proto.upper(), 'blue'),
                                colored(len(protocols[proto]), 'green'))
    pr(text)
    pr('Down: ' + colored(len(down), 'cyan'))
    pr('Total tried: ' + colored(len(working) + len(down), 'cyan'))
    print()


def sort_protocols(working: List[CheckResult]) -> Dict[str, list]:
    x = {}
    for p in PROXY_TYPES:
        x.update({p: []})

    for i in working:
        x[i.proto].append(i)
    return x


def collect_results(threads: list):
    working, down = [], []
    for i in range(Config.threads):
        working += threads[i].working
        down += threads[i].down
    return working, down


def load_list() -> (Generator[str, None, None], None):
    pr('Loading proxies..', '*')
    file = join(Config.workdir, Config.list_file)
    if not isfile(file):
        pr('No such file: ' + file, 'X')
        return

    with open(file) as f:
        for pip in f:
            pip = pip.strip()
            if not _check_proxy_format(pip):
                pr('Bad proxy format: "%s", skipping!' % pip, '!')
                continue
            yield pip


def proxion():
    proxies_to_check = list(load_list())
    if not proxies_to_check:
        pr('Seems we are out of fresh proxies!', '!')
        return

    # Start threading
    threads = []
    pr('Checking %s proxies on %s threads' % (
        colored(len(proxies_to_check), 'green'), colored(Config.threads, 'cyan')))
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
