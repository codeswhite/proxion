
from ipaddress import AddressValueError, IPv4Address
from subprocess import call

from .conf import Config

from termcolor import colored, cprint


def is_ip_address(ip: str) -> bool:
    try:
        IPv4Address(ip)
        return True
    except AddressValueError:
        return False


# Check that the given proxy is a string and has a valid address + port
def check_proxy_format(proxy) -> bool:
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
