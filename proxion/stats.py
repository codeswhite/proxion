from json import loads, dumps, JSONDecodeError
from os.path import join, isfile
from typing import List, Dict, Tuple

from .checker import CheckResult
from .conf import Config

from interutils import pr


class Stat:
    def __init__(self, pip: str, json: Dict[str, dict]):
        # Deserialize
        self.pip = pip
        self.proto = json['proto']
        self.loc = json['loc']
        self.updates = json['updates']

    def update(self, stamp: float, is_up=None):
        if is_up is None:
            is_up = [False]
        self.updates.update({stamp: is_up})

    def serialize(self):
        return {self.pip: {'proto': self.proto,
                           'loc': self.loc,
                           'updates': self.updates}}


def create_stat(result: CheckResult, timestamp: float):
    # New stat from CheckResult
    return Stat(result.pip,
                json={'proto': result.proto,
                      'loc': result.country + ', ' + result.city,
                      'updates': {timestamp: [True, result.time_took]}})


def load_stats() -> (List[Stat], None):
    file = join(Config.workdir, Config.stats_file)
    if not isfile(file):
        return

    try:
        with open(file) as f:
            json = loads(f.read())
    except JSONDecodeError:
        return
    if not json:
        return

    stats = []
    for k in json:
        stats.append(Stat(k, json[k]))
    return stats


def save_stats(stats: List[Stat]) -> None:
    pr('Saving stats..', '*')
    file = join(Config.workdir, Config.stats_file)

    json = {}
    for s in stats:
        json.update(s.serialize())

    with open(file, 'w') as f:
        f.write(dumps(json))


def update_stats(timestamp: float, results: Tuple[List[CheckResult], List[str]]) -> None:
    pr('Updating stats..', '*')

    stats = load_stats()
    if stats is None:
        pr('No stats file found, creating new', '*')
        stats = []
    for down in results[1]:
        for stat in stats:
            if stat.pip == down:
                stat.update(timestamp)
    for working in results[0]:
        for stat in stats:
            if working.pip == stat.pip:
                stat.update(timestamp, [True, working.time_took])
        else:
            stats.append(create_stat(working, timestamp))
    save_stats(stats)
