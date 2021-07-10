from typing import Tuple, List, Iterable, Union, Set
from string import digits
from random import choice
from time import time

from proxion.util import Proxy
from proxion import Defaults


def parse_time_string(time_str: str) -> int:
    time_map = {
        's': 1,
        'm': 60,
        'h': 60 * 60,
        'd': 60 * 60 * 24,
        'w': 60 * 60 * 24 * 7,
        'mo': 60 * 60 * 24 * 30,
        'y': 60 * 60 * 24 * 365,
    }
    for frame in time_map:
        if time_str.endswith(frame):
            quantity = int(time_str.split(frame)[0])
            return time_map[frame] * quantity
    raise ValueError


class CheckerFilter:
    protocols: Set[str]  # = Defaults.checker_proxy_protocols,
    stale: int
    latency: int
    exit_country: str
    strict: bool

    def __init__(self, protocols: Set[str],
                 stale: str, latency: str,
                 exit_country: str, strict: bool):

        # Verify `protocols` are among the options
        if protocols:
            for p in protocols:
                if p not in Defaults.checker_proxy_protocols:
                    raise ValueError(f'Invalid protocol requested: "{p}"')
        self.protocols = protocols

        # Verify `stale` ends with valid characters
        if stale:
            try:
                stale = parse_time_string(stale)
            except ValueError:
                raise ValueError(f'Invalid stale value passed: "{stale}"')
        self.stale = stale

        # Verify `exit_country` is in valid format
        if exit_country:
            if not len(exit_country) != 2:
                raise ValueError(
                    f'Invalid exit country format: "{exit_country}" should be in XX notation (e.g. US, UK)')
        self.exit_country = exit_country

        self.latency = latency
        self.strict = strict

    def build_joblist(self, checklist, no_shuffle: bool) -> List[Tuple[Union[Proxy, str]]]:
        '''Aggregate, randomize and enqueue jobs (checks)'''
        jobs = []
        for proxy in checklist:
            proxy: Proxy

            # Filter exit_country:
            if self.exit_country:
                if not proxy.exit_country:
                    if self.strict:
                        continue
                elif self.exit_country != proxy.exit_country:
                    continue

            # Filter latency:
            if self.latency:
                if not proxy.last_lat:
                    if self.strict:
                        continue
                else:
                    if self.latency < 0:
                        if proxy.last_lat > -self.latency:
                            continue
                    elif proxy.last_lat < self.latency:
                        continue

            # Filter stale
            if self.stale:
                if not proxy.last_check:
                    if self.strict:
                        continue
                elif time() < proxy.last_check + self.stale:
                    print(
                        'DBG skipping proxy because of lastcheck + stale > time()')
                    continue

            # Filter protocols to check
            protos_to_check = None
            if proxy.protos:
                protos_to_check = proxy.protos
            elif not self.strict:
                protos_to_check = Defaults.checker_proxy_protocols

            if self.protocols:
                protos_to_check = set(protos_to_check & self.protocols)

            for proto in protos_to_check:
                # Randomize job list
                pos = 0
                jobs_count = len(jobs)
                if not no_shuffle and jobs_count > 1:
                    pos = choice(range(jobs_count))
                jobs.insert(pos, (proxy, proto))
        return jobs
