import threading
from json.decoder import JSONDecodeError
from random import shuffle
from time import time

from .conf import Config

import requests
from termcolor import colored
from interutils import pr


class CheckResult:
    def __init__(self, pip, protocol, json_response, time_took):
        self.pip = pip
        self.proto = protocol
        self.time_took = time_took

        # Get JSON vars
        self.hostname = json_response['hostname'] if 'hostname' in json_response else None
        self.city = json_response['city']
        self.region = json_response['region']
        self.country = json_response['country']
        self.loc = json_response['loc']
        self.org = json_response['org']


def create_proxy_dict(pip: str, proto: str, ep_proto: str) -> dict:
    return {ep_proto: proto + '://' + pip}


def perform_check(protocol: str, pip: str) -> (CheckResult, None):
    try:
        endpoint_protocol = protocol if protocol == 'http' else 'https'
        t = time()
        # Attempt to get our current IP (use the proxy), expect JSON data!
        resp = requests.get(endpoint_protocol + '://ipinfo.io',
                            proxies=create_proxy_dict(pip, protocol, endpoint_protocol),
                            timeout=Config.timeout)
        t = time() - t
        try:
            # Attempt to decode the received data
            json = resp.json()
            try:
                return CheckResult(pip, protocol, json, t)
            except KeyError as e:
                pr('Result parsing "%s":' % e + json, '*')
        except JSONDecodeError as e:
            # Any failure will be a sign of the proxy not forwarding us,
            # but instead returning some custom data to us!
            pr('Status Code: %d, Text: \n%s' % (resp.status_code, resp.text), '*')
            pr('An JSON Decode error "%s" occurred!' % e, '*')
    except requests.ConnectionError:
        pr('%s failed for %s' % (colored(protocol, 'blue'), colored(pip, 'green')), '*')
    except requests.ReadTimeout:
        pr('%s timed out for %s' % (colored(protocol, 'blue'), colored(pip, 'green')), '*')
    except requests.exceptions.InvalidSchema:
        pr('SOCKS dependencies unmet!', 'X')
        exit(-1)
    return None


class CheckerThread(threading.Thread):
    def __init__(self, proxies_to_check: list):
        super(CheckerThread, self).__init__()
        if not Config.dont_shuffle:
            shuffle(proxies_to_check)
        self.proxies_to_check = proxies_to_check
        self.working, self.down = [], []

    def run(self):
        # try
        while len(self.proxies_to_check) > 0:
            pip = self.proxies_to_check.pop(0)
            pr('Thread %s took: %s' % (colored(self.name, 'cyan'), colored(pip, 'green')), '*')

            for p in Config.protocols:
                r = perform_check(p, pip)
                if r is not None:
                    pr('Working %s proxy @ ' % colored(r.proto, 'blue') + colored(pip, 'green'), '*')
                    self.working.append(r)
                    break
            else:
                pr('Proxy is down!', '*')
                self.down.append(pip)
        # except Exception as e:
        #     pr('An "%s" exception occurred on %s!' % (e, colored(self.name)), 'X')
        #     print(pip)
