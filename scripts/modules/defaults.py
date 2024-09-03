#!/usr/bin/env python3
#
#

from time import time
import pytz
import os

timezone = pytz.timezone("Europe/Amsterdam")

datadir = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../data'))
cachedir = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../cache'))

if __name__ == "__main__":
    print(f"Default timezone is {timezone}")
    print(f"Default directory for storing/saving/committing downloaded files: {datadir}")
    print(f"Default directory for caching files: {cachedir}")
