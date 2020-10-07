#!/usr/bin/env python3
#
from string import Template
from os import listdir
from os.path import isfile, join, basename

templatedir = '../docs/templates'
outputdir = '../docs'

# Get data from other scripts here
d = dict(who='rolf')

def getTemplates(templatedir):
    templates = []
    for f in [f for f in listdir(templatedir) if (f.__contains__('.template.') and isfile(join(templatedir, f)))]:
        templates.append(join(templatedir, f))
    return templates

for tin in getTemplates(templatedir):
    tout = join(outputdir, basename(tin.replace('.template.','.')))
    print(tin + ' -> ' + tout)

    with open(tin, 'r') as templatefile:
        template = templatefile.read()
        
    with open(tout, 'w') as outputfile:
        outputfile.write(Template(template).substitute(d))
