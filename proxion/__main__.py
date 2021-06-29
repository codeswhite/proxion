#!/usr/bin/env python3
from random import choice

from .conf import Config
from .proxion import proxion, banner

from termcolor import cprint
from interutils import pr, clear


def main():
    try:
        Config().init()
        clear()
        cprint(banner + '\n', choice(('red', 'green', 'blue')))
        proxion()  # Enter the Matrix
    except KeyboardInterrupt:
        print()
        pr('Interrupted, exiting!', '!')
    # except Exception as e:
    #     prl(f'An "{e}" exception occurred on the main thread!', 'X')


if __name__ == "__main__":
    exit(main())
