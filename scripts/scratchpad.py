#!/usr/bin/env python3
#
from matplotlib import pyplot as plt
from dateutil import parser
from statistics import mean
import datetime
import csv
import json
import modules.brondata as brondata
from modules.brondata import decimalstring, smooth
from scipy.ndimage.filters import uniform_filter1d
from operator import itemgetter

#brondata.freshdata()
metenisweten = brondata.readjson('../cache/daily-stats.json')

def sortDictOnKey(dictionary):
    return dict(sorted(metenisweten.items(), key=itemgetter(0)))

print(str(sortDictOnKey(metenisweten)))
