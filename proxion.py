from threading import active_count
from time import sleep, time

from checker import CheckerThread
from conf import Config
from disk import proxy_list, stat
from utils import prl, PRL_VERB, PRL_WARN, cyan


def main():
    proxies_to_check = list(proxy_list.load_list())
    if not proxies_to_check:
        prl('Seems we are out of fresh proxies!', PRL_WARN)
        return

    # Start threading
    threads = []
    prl('Checking %s proxies on %s threads' % (cyan(len(proxies_to_check)), cyan(Config.threads)))
    for i in range(Config.threads):
        threads.append(CheckerThread(proxies_to_check))
        threads[i].setDaemon(True)
        threads[i].start()
        # sleep(0.1)
    try:
        while active_count() - 1:
            sleep(5)
            prl("%s active threads..." % cyan(active_count() - 1), PRL_VERB)
            # TODO A pretty print that will show how many tried, how many failed (by different readsons) and how many from each pprotocol
        prl("All threads done.")
    except KeyboardInterrupt:
        print()
        prl('Interrupted!', PRL_WARN)
    finally:
        prl('Saving checked..')
        timestamp = time()
        w, d = [], []
        for i in range(Config.threads):
            w += threads[i].working
            d += threads[i].down
        stat.update_stats(timestamp, w, d)


if __name__ == '__main__':
    try:
        c = Config()  # Initialize configuration
        # TODO print banner
        c.parse_args()  # Parse arguments
        main()  # Enter the Matrix
    except KeyboardInterrupt:
        print()
        prl('Interrupted, exiting!', PRL_WARN)
    # except Exception as e:
    #     prl('An "%s" exception occurred on the main thread!' % e, PRL_ERR)
