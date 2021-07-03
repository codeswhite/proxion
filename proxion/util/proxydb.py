from typing import Iterable, List
from random import shuffle
from pathlib import Path
from threading import Lock

from interutils import DictConfig

from proxion.util import Proxy


class ProxyDB:
    '''
    This is a low level db interface, expect exceptions to rise

    The ProxyDB is in a form of:
    {
        '0.0.0.0:00000': {
            'type': 'https',
            'last_check': None,
            'latency': 90,
        },
        '1.2.3.4:54321': {
            'type': 'socks',
            'last_check': time.time(),
            'latency': 320,
        }
    }
    '''

    @classmethod
    def __init__(cls, db_file_path: Path):
        lock = Lock()
        lock.acquire()
        cls.dict_config = DictConfig(db_file_path, {}, quiet=True)
        lock.release()
        cls._l = lock

    @classmethod
    def update_one(cls, proxy: Proxy, save: bool = True) -> int:
        if not proxy:
            return

        cls.dict_config.update(proxy.serialize())
        if save:
            cls._save_state()
        return 1

    @classmethod
    def update_some(cls, proxies: Iterable[Proxy]) -> int:
        if not proxies:
            return

        count = 0
        for proxy in proxies:
            count += cls.update_one(proxy, save=False)

        cls._save_state()
        return count

    @classmethod
    def remove_one(cls, proxy: Proxy, save: bool = True) -> int:
        if not proxy:
            return

        cls.dict_config.pop(proxy.pip)
        if save:
            cls._save_state()
        return 1

    @classmethod
    def remove_some(cls, proxies: Iterable[Proxy]) -> int:
        if not proxies:
            return

        count = 0
        for proxy in proxies:
            count += cls.remove_one(proxy, save=False)

        cls._save_state()
        return count

    @classmethod
    def _save_state(cls):
        cls._l.acquire()
        cls.dict_config.save()
        cls._l.release()

    @classmethod
    def is_in(cls, pip: str) -> bool:
        return pip in cls.dict_config

    @classmethod
    def get_proxy(cls, pip: str) -> Proxy:
        return deserialize(pip, cls.dict_config[pip])

    @classmethod
    def get_proxy_dict(cls):
        return dict(cls.dict_config)

    @classmethod
    def get_proxies(cls, do_shuffle: bool = True) -> List[Proxy]:
        '''
        Get proxies from DB in deserialized form (Proxy struct)
        '''
        temp = cls.get_proxy_dict()
        if do_shuffle:
            try:
                shuffle(temp)
            except KeyError:
                pass
        lst = []
        for key, val in temp.items():
            lst.append(deserialize(key, val))
        return lst


def deserialize(pip: str, info: dict) -> Proxy:
    proxy = Proxy(pip)
    for key, val in info.items():
        if key == 'protos':
            if val:
                val = set(val)
            else:
                val = set()
        proxy.__setattr__(key, val)
    return proxy
