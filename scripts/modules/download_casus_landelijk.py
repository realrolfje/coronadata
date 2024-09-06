#!/usr/bin/env python3
#
# WARNING: LARGE DOWNLOAD, 1.6GB AND COUNTING
# Downloads https://data.rivm.nl/covid-19/COVID-19_casus_landelijk.json 
#
# Also writes the "testpunten.json" file in the cache directory, see below

import os
from utilities import downloadIfStale, readjson, writejson
from defaults import cachedir
from metenisweten import initrecord
from datecache import dateCache


def download(force=False):
    filename = os.path.join(cachedir, "COVID-19_casus_landelijk.json")
    if downloadIfStale(
        filename=filename,
        url="https://data.rivm.nl/covid-19/COVID-19_casus_landelijk.json",
        force = force):
        return filename
    else:
        return None


def store(downloaded_file):
    if downloaded_file == None:
        return    

    testpunten = {}
    for record in readjson(downloaded_file):
        if not dateCache.isvaliddate(record['Date_statistics'], filename):
            continue

        todaysRecord = initrecord(record['Date_statistics'])

        todaysRecord['positief'] += 1

        # https://data.rivm.nl/meta/srv/dut/catalog.search#/metadata/2c4357c8-76e4-4662-9574-1deb8a73f724?tab=general
        # -	In versie 2 van deze dataset is de variabele ‘hospital_admission’ niet meer beschikbaar. Voor het aantal
        # ziekenhuisopnames wordt verwezen naar de geregistreerde ziekenhuisopnames van Stichting NICE
        # (https://data.rivm.nl/covid-19/COVID-19_ziekenhuisopnames.html).
        # try:
        #     if 'Hospital_admission' in record and (record['Hospital_admission'] == "Yes"):
        #         todaysRecord['opgenomen'] += 1
        # except KeyError:
        #     print(record)
        #     raise

        todaysRecord['rivm-datum'] = record['Date_file']

        if (record['Deceased'] == 'Yes'):
            todaysRecord['overleden'] += 1

        try:
            # Age groups are 0-10, 10-20, 30-40 etc, we make that 5, 15, 25, 35.
            age = int(record['Agegroup'].split('-')[0].split('+')[0])+5
            if age not in todaysRecord['besmettingleeftijd']:
                todaysRecord['besmettingleeftijd'][age] = 1
            else:
                todaysRecord['besmettingleeftijd'][age] += 1
        except ValueError:
            # print('ERROR '+record['Date_statistics'] + ' | ' + record['Agegroup'])
            pass

        testpunt = record['Municipal_health_service']
        if testpunt not in testpunten:
            testpunten[testpunt] = 1
        else:
            testpunten[testpunt] += 1

    writejson(os.path.join(cachedir, 'testlocaties.json'), testpunten)


def process(force=False):
    """Download and process the data"""
    store(download(force))

if __name__ == "__main__":
    process(force=True)
    dateCache.cacheReport()
