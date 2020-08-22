#!/usr/bin/env python3
#
# Haalt COVID-19 testresultaten op bij RIVM
#

import urllib.request
import os.path
import time
import json

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

# Not used yet, maybe handy to graph more stuff based on a single json
def builddaily():
    with open('../cache/COVID-19_casus_landelijk.json', 'r') as json_file:
        data = json.load(json_file)
        metenisweten = {}
        for record in data:
            if (record['Date_statistics'] not in metenisweten):
                metenisweten[record['Date_statistics']] = {
                    'positief': 0,
                    'nu_op_ic': 0,
                    'opgenomen' : 0
                }
            metenisweten[record['Date_statistics']]['positief'] += 1

            if (record['Hospital_admission'] == "Yes"):
                metenisweten[record['Date_statistics']]['opgenomen'] += 1
                totaal_opgenomen += 1

            # metenisweten[record['Date_statistics']] = record['Agegroup']

            metenisweten[record['Date_statistics']]['rivm-datum'] = record['Date_file']


    with open('../cache/NICE-intake-count.json', 'r') as json_file:
        data = json.load(json_file)
        for record in data:
            if (record['date'] not in metenisweten):
                metenisweten[record['date']] = {
                    'positief': 0,
                    'nu_op_ic': 0,
                    'opgenomen' : 0
                }
            metenisweten[record['date']]['nu_op_ic'] += record['value']


if __name__ == "__main__":
    download()
