
from ipaddress import AddressValueError, IPv4Address


PROXY_TYPES = ('socks5', 'socks4', 'https', 'http')


def is_proxy_format(proxy) -> bool:
    ''' Check that the given proxy is a string and has a valid address + port '''

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
