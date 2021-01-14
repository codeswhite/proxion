#!/usr/bin/env python3
from random import choice

from .conf import Config
from .proxion import proxion, banner

from termcolor import colored, cprint
from interutils import pr, clear

def main():
    try:
        c = Config()  # Initialize configuration
        clear()
        cprint(banner, choice(('red', 'green', 'blue')))
        c.parse_args()  # Parse arguments
        proxion()  # Enter the Matrix
    except KeyboardInterrupt:
        print()
        pr('Interrupted, exiting!', '!')
    # except Exception as e:
    #     prl('An "%s" exception occurred on the main thread!' % e, 'X')


if __name__ == "__main__":
    exit(main())
