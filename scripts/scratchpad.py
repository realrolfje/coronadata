#!/usr/bin/env python3
#
from matplotlib import pyplot as plt

from modules.brondata import dateCache


datestr ='2021-06-19'
print(datestr)
print(dateCache.parse(datestr))

