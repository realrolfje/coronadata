#!/usr/bin/env python3
#
from string import Template
from os import listdir
from os.path import isfile, join, basename
from modules.brondata import decimalstring

d = dict(who='rolf')

print(listdir())

print(decimalstring(1000))
print(decimalstring(10000))
print(decimalstring(10.2))
print(decimalstring(10000.2))
