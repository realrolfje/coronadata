#!/usr/bin/env python3
#
from string import Template
from os import listdir
from os.path import isfile, join

d = dict(who='rolf')

templates = [f for f in listdir('.') if (f.endswith('.template') and isfile(join('.', f)))]

for tin in templates:
    tout = tin[:-9]
    with open(tin, 'r') as templatefile:
        template = templatefile.read()
        
    with open(tout, 'w') as outputfile:
        outputfile.write(Template(template).substitute(d))
