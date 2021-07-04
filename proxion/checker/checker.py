from random import choice
from time import sleep, time
from typing import Iterable, Dict, List, Tuple
from json.decoder import JSONDecodeError
import multiprocessing as mp
import os
import urllib3

import requests
from termcolor import colored
from interutils import cyan, pr

from proxion.util import (
    Proxy,
)
from proxion import Defaults


urllib3.disable_warnings()


class ProxyChecker:
    '''
    Manages the whole process of checking:

    Proxy checked first receives an array of parameters
    Then we aggregate shuffle and 

    '''

    def __init__(self, checklist: Iterable[Proxy],
                 max_threads: int = Defaults.checker_max_threads,
                 protocols: Tuple[str] = Defaults.checker_proxy_protocols,
                 timeout: int = Defaults.checker_timeout,
                 no_shuffle: bool = False,
                 verbose: bool = False):

        self.timeout = timeout
        self.verbose = verbose

        if max_threads < 1:
            raise ValueError(f'Invalid thread count: {max_threads}')
        if not protocols:
            raise ValueError('Please specify at least one protocol!')
        if not checklist:
            raise ValueError('No proxies to check!')

        # Aggregate, randomize and enqueue jobs (checks)
        jobs = []
        for proxy in checklist:
            # Get proxies to check
            protos_to_check = Defaults.checker_proxy_protocols
            if proxy.protos:
                protos_to_check = proxy.protos
            protos_to_check = [
                p for p in protos_to_check if p in protocols]

            for proto in protos_to_check:
                # Randomize job list
                pos = 0
                jobs_count = len(jobs)
                if not no_shuffle and jobs_count > 1:
                    pos = choice(range(jobs_count))
                jobs.insert(pos, (proxy, proto))

        self.queue = mp.Queue()
        for job in jobs:
            self.queue.put(job)

        jobs_count = len(jobs)
        max_threads = min(max_threads, jobs_count)
        pr(f'Checking {cyan(len(checklist))} proxies ({cyan(jobs_count)} jobs) on {cyan(max_threads)} threads')

        self._terminate_flag = False
        with mp.Manager() as manager:
            self.up = manager.list()
            self.jobs_done = manager.Value('i', 0)

            self.procs = []
            for _ in range(max_threads):
                self.procs.append(p := mp.Process(
                    target=self.worker, daemon=True))
                p.start()

            termination_print_interval = 2
            print_interval = 3
            last_print = time()
            try:
                while self.active_children():
                    sleep(0.25)
                    if self.verbose and time() - last_print > print_interval:
                        last_print = time()
                        pr(f'Jobs done: [{self.jobs_done.value}/{jobs_count}] = {100 * int(self.jobs_done.value) / jobs_count}%', '*')
                        self.show_status()

            except KeyboardInterrupt:
                print()
                pr('Interrupted, Killing children!', '!')
                self._terminate_flag = True
                self.queue.close()
                for p in self.procs:
                    p.kill()

                while n_alive := self.active_children():
                    sleep(0.25)
                    if time() - last_print > termination_print_interval:
                        last_print = time()
                        pr(f'Waiting for {cyan(n_alive)} children to exit', '*')
                        pr(f'Jobs done: [{self.jobs_done.value}/{jobs_count}] = {100 * int(self.jobs_done.value) / jobs_count}%', '*')

            finally:
                # pr('Joining remaining procs')
                # pool.join()
                pr('All children exited')
                self.show_status()
                # update_stats(time(), self.collect_results())

    def active_children(self) -> int:
        if not self.procs:
            return 0
        return list(map(lambda p: p.is_alive(), self.procs)).count(True)

    def worker(self):
        while not self.queue.empty():
            if self._terminate_flag:
                pr('Terminating child although queue is not empty yet', '!')
                break

            proxy, proto = self.queue.get()
            proxy: Proxy
            proto: str

            if self.verbose:
                pr(f'Thread {cyan(os.getpid())} checking: {cyan(proxy.pip)} for proto: {cyan(proto)}', '*')

            res = self.perform_check(proxy.pip, proto)
            self.jobs_done.value += 1
            if res is not None:
                pr(f'Working {cyan(", ".join(res.protos))} proxy @ {colored(proxy.pip, "green")}')
                self.up.append(res)
                break

    def perform_check(self, pip: str, protocol: str) -> (Proxy, None):
        try:
            proxies_dict = {
                protocol if protocol == 'http' else 'https': protocol + '://' + pip
            }

            _t = time()
            # Attempt to get our current IP (trough the proxy), expect JSON data!
            resp = requests.get('https://ipinfo.io/', proxies=proxies_dict,
                                timeout=self.timeout, verify=False)
            latency = time() - _t
            try:
                # Attempt to decode the received data
                json = resp.json()
                try:
                    return Proxy(pip, (protocol,), time(), latency, json['country'])
                except KeyError as err:
                    pr(f'Result parsing "{err}" from:' + json, '*')
            except JSONDecodeError as err:
                # Any failure will be a sign of the proxy not forwarding us,
                # but instead returning some custom data to us!
                pr(f'Status Code: {resp.status_code}, Text: \n{resp.text}', '*')
                pr(f'An JSON Decode error "{err}" occurred!', '*')

        except (requests.ConnectTimeout, requests.ReadTimeout):
            pr(f'{cyan(pip)} -> {cyan(protocol)} timed out', '*')
        except requests.ConnectionError:
            pr(f'{cyan(pip)} -> {cyan(protocol)} connection error', '*')
        except requests.exceptions.InvalidSchema:
            pr('SOCKS dependencies unmet!', 'X')
        except ValueError as err:
            if err.args[0] == 'check_hostname requires server_hostname':
                pr(f'{cyan(pip)} -> {cyan(protocol)} TLS error, proxy is probably HTTP', '*')

    def show_status(self) -> None:

        def _sort_protocols(working: List[Proxy]) -> Dict[str, list]:
            ''' Sort proxies by ProxyType'''
            dic = {}
            for proto in Defaults.checker_proxy_protocols:
                dic.update({proto: []})

            for proxion in working:
                for proto in proxion.protos:
                    dic[proto].append(proxion)
            return dic

        ''' Show status (using the collected results) '''
        working = self.up
        text = 'Working:'
        for proto, proxies in _sort_protocols(working).items():
            if proxies:
                text += f' {cyan(proto.upper())}:{cyan(len(proxies))}'
        pr(text)
        print()
