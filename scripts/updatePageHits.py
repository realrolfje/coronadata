#!/usr/bin/env python3
#
import urllib.request
from urllib.error import URLError, HTTPError
import re 
from datetime import datetime
from modules.brondata import logError

#  <img src="https://counter.blakedrumm.com/count/tag.svg?url=https%3A%2F%2Frealrolfje.github.io%2Fcoronadata%2F" alt="Hits">
url="https://counter.blakedrumm.com/count/tag.svg?url=https%3A%2F%2Frealrolfje.github.io%2Fcoronadata%2F"

try:
    with urllib.request.urlopen(url) as response:
        body = str(response.read())
        counter=re.search('>[\.,0-9]+</', body).group(0)[1:-2]
        date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        print("https://realrolfje.github.io/coronadata/ has "+counter+" total pagehits.")

    filename="../data/pagehits.csv"
    with open(filename, "a") as file_object:
        file_object.write(date+';'+counter+'\n')

except HTTPError as e:
    logError("Problem opening '%s': http error %d, %s" % (url, e.code, e.reason))
except URLError as e:
    logError("Problem opening '%s': %s" % (url, e.reason))
