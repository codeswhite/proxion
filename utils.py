#!/usr/bin/env python3
###
##
#

from subprocess import call, check_output, DEVNULL, CalledProcessError

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


def ask(question: str) -> (None, str):
    """
    Ask the user something
    :param question:
    :return: the response, None if no response
    ** Expect a KeyboardInterrupt!!
    """
    prl(question, PRL_CHOICE)
    answer = input('>')
    if answer == '':
        return None
    try:
        answer = int(answer)
    except ValueError:
        pass
    return answer


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


def cyan(text) -> str:
    return colored(str(text), 'cyan')


def banner(txt: str, style: str = 'slant') -> str:
    """
    Depends on: "pyfiglet"
    :param txt: The text to return as an ASCII art
    :param style: The style (From: /usr/lib/python3.6/site-packages/pyfiglet/fonts/)
    :return: The created ASCII art
    """
    try:
        from pyfiglet import Figlet
    except ImportError:
        prl('Module "pyfiglet" not installed, rendering legacy banner', PRL_ERR)
        return '~=~=~ %s ~=~=~' % txt
    f = Figlet(font=style)
    return f.renderText(text=txt)


def get_date() -> str:
    """
    :return: today's date (e.g. "28.11.2017" ;P)
    """
    from datetime import datetime
    return datetime.now().strftime("%d.%m.%Y")


# def is_mac(mac: str) -> bool:
#     """
#     Check if the specified string is a mac address
#     Bytes delimiter can be either '-' or ':'
#     The MAC string is stripped.
#     :param mac: The MAC address string
#     :return: True if the MAC address is valid
#     """
#     return bool(match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.strip().lower()))


def is_package(package_name) -> (str, None):
    """
    Check if a system package is installed

    :param package_name: Package to check
    :return: The version of the installed package or None if no such package
    """
    try:
        return check_output(['/usr/bin/pacman', '-Q', package_name], stderr=DEVNULL).decode().strip().split(' ')[1]
    except CalledProcessError:
        pass
    try:
        return check_output(('apt', 'list', '-qq', package_name)).decode().split(' ')[1]
    except CalledProcessError:
        pass
    return None


# def get_net() -> (None, dict):
#     # Uses iproute2 (ip)
#
#     # Example raw:
#     # default via 192.168.1.1 dev eth0
#     # 192.168.1.0/24 dev eth0 proto kernel scope link src 192.168.1.28
#
#     raw = check_output(['ip', 'route']).decode().strip().split('\n')
#     d = {}
#     if not raw or 'default' not in raw[0]:
#         return None  # No route
#     else:
#         d.update({'default': raw[0].split(' ')[2:5:2]})  # default: (gateway, interface)
#
#     for li in raw[1:]:
#         ls = li.split(' ')
#         d.update({ls[2]: {'interface': ls[2], 'subnet': ls[0], 'ip': ls[8]}})
#
#     return d


def ping(ip: str, count: int = 1, timeout: int = 1) -> bool:
    """
    Depends on: "iputils"
    A binding for system call ping
    :param ip: Destination
    :param count: How much ping requests to send
    :param timeout: How long wait for a reply
    :return: A boolean that represents success of the ping
    """
    if count < 1:
        raise ValueError('Count cannot be lower than 1')
    try:
        return call(['ping', '-c', str(count), '-w', str(timeout), ip], stdout=DEVNULL, stderr=DEVNULL) == 0
    except CalledProcessError:
        pass
    except KeyboardInterrupt:
        prl('[utils] Ping interrupted!', PRL_WARN)
    return False


# Check that the given proxy is a string and has a valid address + port
def check_proxy_format(proxy_to_check):
    if type(proxy_to_check) is not str:
        return False
    x = proxy_to_check.strip().split(':')
    if len(x) != 2:
        return False
    ip, port = x
    try:
        port = int(port)
    except ValueError:
        return False
    if port < 0 or port > 65535:
        return False
    # TODO: Add ip address verity check
    return True
