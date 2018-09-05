# proxion

Automated multi-threaded proxy checker with uptime and latency statistics

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Cloning

First you may clone the project into your local storage:

```
git clone https://github.com/WhiteOnBlackCode/proxion
cd proxion
```

### Virtual Environment

This step is optional yet recommended by many.

You may install python-virtualenv package by using pip:

```
pip install virtualenv
```

To create a new virtual environment in current directory:

```
virtualenv .
```

Afterwards you'll be able to activate the virtual environment:

```
source venv/bin/activate
```

### Dependencies

The script is built for python3 and requires few python packages:
* requests
* PySocks
* termcolor

Install required packages with pip --requirement switch:

```
pip install -r requirements.txt
```

### Usage

```
python3 proxion.py --help
```

## Notes

The script will create 'proxies' directory in home directory and will expect to find there 'proxylist.txt'
