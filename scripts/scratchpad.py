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
import urllib.request

url="https://hitcounter.pythonanywhere.com/count/tag.svg?url=https%3A%2F%2Frealrolfje.github.io%2Fcoronadata%2F"
filename="counter.svg"

with urllib.request.urlopen(url) as response:
   html = str(response.read())
   print(html)
