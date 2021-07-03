from site import USER_BASE
from ipaddress import AddressValueError, IPv4Address
from pathlib import Path
from random import choice

from termcolor import cprint
from interutils import clear


banner = Path(USER_BASE).joinpath(
    'proxion', 'assets', 'banner.txt').read_text()


def print_banner(clean: bool = True) -> None:
    if clean:
        clear()
    cprint(banner + '\n', choice(('red', 'green', 'blue')))


class InvalidProxyFormatError(Exception):
    pass


def is_ip_address(ip_addr: str) -> bool:
    try:
        IPv4Address(ip_addr)
        return True
    except AddressValueError:
        return False


def is_proxy_format(pip: str) -> bool:
    ''' Check that the given proxy is a string and has a valid address + port '''

    if not isinstance(pip, str):
        return False

    pts = pip.strip().split(':')
    if len(pts) != 2:
        return False
    ip_addr, port = pts

    try:
        port = int(port)
    except ValueError:
        return False
    if port < 0 or port > 65535:
        return False
    if not is_ip_address(ip_addr):
        return False

    return True
