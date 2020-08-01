#!/usr/bin/env python3
#
# Haalt COVID-19 testresultaten op bij RIVM
#

import urllib.request
import os.path
import time

def downloadIfStale(filename, url):
    if os.path.isfile(filename) and os.stat(filename).st_mtime > ( time.time() - 3600):
        print(filename+" exists.")
    else:
        print("Downloading data to "+filename)
        urllib.request.urlretrieve(url, filename)


def download():
    downloadIfStale(
        '../cache/COVID-19_casus_landelijk.json',
        'https://data.rivm.nl/covid-19/COVID-19_casus_landelijk.json'
    )
    downloadIfStale(
        '../cache/NICE-intake-cumulative.json',
        'https://www.stichting-nice.nl/covid-19/public/intake-cumulative/'
    )
    downloadIfStale(
        '../cache/NICE-intake-count.json',
        'https://www.stichting-nice.nl/covid-19/public/intake-count/'
    )

if __name__ == "__main__":
    download()
