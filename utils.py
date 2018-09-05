#!/usr/bin/env python3
###
##
#

from ipaddress import AddressValueError, IPv4Address

from termcolor import colored, cprint

from conf import Config

PRL_WARN = ('yellow', '!')
PRL_SU = ('yellow', '#')
PRL_ERR = ('red', 'X')
PRL_CHOICE = ('cyan', '?')
PRL_HEAD = ('cyan', '')
PRL_VERB = ('blue', '~')


def prl(text: str, lvl: iter = ('green', '+'), attrib: list = ()) -> None:
    if not Config.verbose and lvl == PRL_VERB:
        return

    text = str(text)
    if lvl == PRL_HEAD:
        a = list(attrib)
        if attrib:
            a.insert(0, 'bold')
        cprint(text, lvl[0], attrs=a)
    else:
        print(colored('[%s] ' % lvl[1], lvl[0], attrs=attrib) + text)


def choose(options: iter = ('Yes', 'No'), prompt: str = 'Choose action:', default: int = 0) -> int:
    if not options:
        raise ValueError(" [!] No options passed to choice() !!!")  # No options
    prl(prompt, PRL_CHOICE)
    for index, option in enumerate(options):
        line = '\t'
        if index == default:
            line += '[%d]. ' % (index + 1)
        else:
            line += ' %d.  ' % (index + 1)
        line += option
        cprint(line, 'yellow')
    try:
        ans = input(colored('>', 'yellow'))
        if not ans:
            return default
        ans = int(ans)
        assert 0 < ans <= len(options)
        return ans - 1
    except KeyboardInterrupt:
        return -2  # Keyboard Interrupt
    except AssertionError:
        return -1  # Bad Number
    except ValueError:
        return -1  # Probably text received


def pause(reason: str, cancel: bool = False):
    s = 'Press %s to %s' % (colored('[ENTER]', 'cyan'), reason)
    if cancel:
        s += ', %s to cancel' % colored('[^C]', 'red')
    prl(s, PRL_CHOICE)

    try:
        input()
        return True
    except KeyboardInterrupt:
        return False


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
