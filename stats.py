from json import loads, dumps, JSONDecodeError
from os.path import join, isfile
from typing import List, Dict

from checker import CheckResult
from conf import Config
from utils import prl, PRL_VERB


class Stat:
    def __init__(self, pip: str, json: Dict[str, dict]):
        self.pip = pip
        self.proto = json['proto']
        self.loc = json['loc']
        self.updates = json['updates']

    def update_stat(self, stamp: float, is_up=None):
        if is_up is None:
            is_up = [False]
        self.updates.update({stamp: is_up})

    def get_json(self):
        return {self.pip: {'proto': self.proto,
                           'loc': self.loc,
                           'updates': self.updates}}


def create_stat(result: CheckResult, timestamp: float):
    # The creation of new stats
    return Stat(result.pip,
                json={'proto': result.proto,
                      'loc': result.country + ', ' + result.city,
                      'updates': {timestamp: [True, result.time_took]}})


def load_stats() -> (list, None):
    prl('Loading stats..', PRL_VERB)
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


def save_stats(stats: list) -> None:
    prl('Saving stats..', PRL_VERB)
    file = join(Config.workdir, Config.stats_file)

    json = {}
    for s in stats:
        json.update(s.get_json())

    with open(file, 'w') as f:
        f.write(dumps(json))


def update_stats(timestamp: float, working: List[CheckResult], down: list) -> None:
    prl('Updating stats..', PRL_VERB)

    stats = load_stats()
    if stats is None:
        stats = []
    for d in down:
        for s in stats:
            if s.pip == d:
                s.update_stat(timestamp)
    for w in working:
        for s in stats:
            if w.pip == s.pip:
                s.update_stat(timestamp, [True, w.time_took])
        else:
            stats.append(create_stat(w, timestamp))
    save_stats(stats)
