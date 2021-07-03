from time import time
from pathlib import Path
from typing import Set

from interutils import pr

from .common import is_proxy_format, InvalidProxyFormatError


def assure_proxy_format(pip: str) -> None:
    res = is_proxy_format(pip)
    if not res:
        raise InvalidProxyFormatError(
            f'Invalid proxy supplied: ProxyIP={pip}')
    return res


class Proxy:
    '''
    A definition of a proxy with info.
    '''
    pip: str
    protos: Set[str]
    last_check: int
    last_lat: int
    exit_country: str

    def __init__(self, pip: str,
                 protos: Set[str] = None,
                 last_check: int = None,
                 last_lat: int = None,
                 exit_country: str = None):
        assure_proxy_format(pip)
        self.pip = pip
        if protos:
            self.protos = set(protos)
        else:
            self.protos = set()
        self.last_check = last_check
        self.last_lat = last_lat
        self.exit_country = exit_country

    def serialize(self) -> dict:
        return {
            self.pip: {
                'protos': list(self.protos),
                'last_check': self.last_check,
                'last_lat': self.last_lat,
                'exit_country': self.exit_country,
            }
        }

    def get_check_delta(self) -> int:
        return time() - self.last_check

    def update(self, other):
        if self.pip != other.pip:
            raise ValueError('Can not update proxy with a different proxy IP!')
        self.protos.update(other.protos)
        self.last_check = other.last_check
        self.last_lat = other.last_lat
        self.exit_country = other.exit_country


def parse_proxies_file(path: Path) -> list:
    buff = []
    for line in path.read_text().splitlines():
        try:
            buff.append(Proxy(line))
        except InvalidProxyFormatError:
            pr(f'Invalid proxy line: {line} in file: {str(path)}', '!')
    return buff
