#!/usr/bin/env python3
#
from string import Template
from os import listdir
from os.path import isfile, join, basename
from modules.brondata import decimalstring


d = dict(who='rolf')

print(listdir())

# Turns US 10,000.00 into EU 10.000,00
def decimalstring(number):
    if number == round(number) and len(str(number)) <= 4:
        return str(number)
    else:
        return "{:,}".format(number).replace(',','x').replace('.',',').replace('x','.')


print(decimalstring(1000))
print(decimalstring(10000))
print(decimalstring(10.2))
print(decimalstring(10000.2))
