#!/usr/bin/env python3
#
from string import Template
import re
print(re.search('-\d{4}$','01-02-0003'))

# Simple templating
d = dict(who='rolf')
print(Template('Give $who $$100').substitute(d))


# This does not work
e = {
    'who' : 'rolf',
    'what' : {
        'currency' : 'eur'
    }
}
print(Template('Give $who $$100 in ${what.currency}').substitute(e))