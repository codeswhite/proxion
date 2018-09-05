from os.path import join, isfile
from random import choice
from threading import active_count
from time import sleep, time
from typing import Generator, Dict, List, Tuple

from checker import CheckerThread, CheckResult
from conf import Config
from stats import update_stats
from utils import prl, PRL_VERB, PRL_WARN, PRL_ERR, check_proxy_format, colored, clear

banner = """
    ____                  _                      
   / __ \_________  _  __(_)___  ____  
  / /_/ / ___/ __ \| |/_/ / __ \/ __ \ 
 / ____/ /  / /_/ />  </ / /_/ / / / / 
/_/   /_/   \____/_/|_/_/\____/_/ /_/  
"""

PROXY_TYPES = ('socks5', 'socks4', 'https', 'http')


def show_status(results: Tuple[List[CheckResult], List[str]]) -> None:
    working, down = results[0], results[1]
    clear(colored(banner, choice(('red', 'green', 'blue'))))
    text = 'Working: '
    protocols = sort_protocols(working)
    for proto in protocols.keys():
        if len(protocols[proto]) > 0:
            text += ' %s:%s' % (colored(proto.upper(), 'blue'), colored(len(protocols[proto]), 'green'))
    prl(text)
    prl('Down: ' + colored(len(down), 'cyan'))
    prl('Total tried: ' + colored(len(working) + len(down), 'cyan'))
    print()


def sort_protocols(working: List[CheckResult]) -> Dict[str, list]:
    x = {}
    for p in PROXY_TYPES:
        x.update({p: []})

    for i in working:
        x[i.proto].append(i)
    return x


def collect_results(threads: list):
    w, d = [], []
    for i in range(Config.threads):
        w += threads[i].working
        d += threads[i].down
    return w, d


def load_list() -> (Generator[str, None, None], None):
    prl('Loading proxies..', PRL_VERB)
    file = join(Config.workdir, Config.list_file)
    if not isfile(file):
        prl('No such file: ' + file, PRL_ERR)
        return

    with open(file) as f:
        for pip in f:
            pip = pip.strip()
            if not check_proxy_format(pip):
                prl('Bad proxy format: "%s", skipping!' % pip, PRL_WARN)
                continue
            yield pip


def main():
    proxies_to_check = list(load_list())
    if not proxies_to_check:
        prl('Seems we are out of fresh proxies!', PRL_WARN)
        return

    # Start threading
    threads = []
    prl('Checking %s proxies on %s threads' % (
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
        prl("All threads done.")
    except KeyboardInterrupt:
        print()
        prl('Interrupted!', PRL_WARN)
    finally:
        prl('Saving checked..')
        update_stats(time(), collect_results(threads))


if __name__ == '__main__':
    try:
        c = Config()  # Initialize configuration
        clear(colored(banner, choice(('red', 'green', 'blue'))))
        c.parse_args()  # Parse arguments
        main()  # Enter the Matrix
    except KeyboardInterrupt:
        print()
        prl('Interrupted, exiting!', PRL_WARN)
    # except Exception as e:
    #     prl('An "%s" exception occurred on the main thread!' % e, PRL_ERR)
