## Proxion
Automated multi-threaded proxy checker with uptime and latency statistics

## Running

### PyPi
Install from PyPI repo (using `pip`)

    $ pip install proxion

### AUR
Install from AUR repo (using any AUR helper like `yay` for example)

    $ yay -S python-proxion

## Usage
After installing on your machine run the script with:

    $ proxion --help

### Notes

The script will create 'proxies' directory in home directory and will expect to find there 'proxylist.txt'

## Contributing
This project welcomes with open arms any intent to contribute in any way :)

The following instructions are for anyone who is interested in setting up the project locally for development/testing purposes:

    $ git clone https://github.com/codeswhite/proxion
    $ cd ./proxion
    $ pipenv install

Note that installing requirements can be **alternatively** done via basic `pip`:

    $ pip install -r requirements.txt
