from os.path import join, isfile
from typing import Generator

from conf import Config
from utils import prl, PRL_VERB, PRL_ERR, check_proxy_format, PRL_WARN


def load_list() -> (Generator[str, None, None], None):
    prl('Loading proxies..', PRL_VERB)
    file = join(Config.workdir, Config.list_file)
    if not isfile(file):
        prl('No such file: ' + file, PRL_ERR)
        return

    with open(file) as f:
        for pip in f:
            pip = pip.strip()
            if not check_proxy_format(pip):
                prl('Bad proxy format: "%s", skipping!' % pip, PRL_WARN)
                continue
            yield pip
