#!/usr/bin/env python3

# Downloads the Rt dataset.
# See data.rivm.nl, Covid-19 reproductiegetal
# See https://data.rivm.nl/meta/srv/dut/catalog.search#/metadata/ed0699d1-c9d5-4436-8517-27eb993eab6e
#
# RIVM:
# Het aantal COVID-19 gerelateerde hospitalisaties is al geruime tijd laag en COVID-19 is per 1 juli
# 2023 geen meldingsplichtige ziekte meer. Daarom wordt de data vanaf 11 juli 2023 niet meer bijgewerkt.
#
import os
from utilities import downloadIfStale, readjson
from defaults import cachedir
from metenisweten import initrecord
from datecache import dateCache


def download(force=False):
    filename = os.path.join(cachedir, "COVID-19_reproductiegetal.json")
    if downloadIfStale(
        filename=filename,
        url="https://data.rivm.nl/covid-19/COVID-19_reproductiegetal.json",
        force = force):
        return filename
    else:
        return None


def store(downloaded_file):
    if downloaded_file == None:
        return    

    data = readjson(downloaded_file)
    for record in data:
        if not dateCache.isvaliddate(record['Date'], os.path.basename(downloaded_file)):
            continue

        m = initrecord(record['Date'])

        if 'Rt_avg' in record:
            m['Rt_avg'] = record['Rt_avg']
        if 'Rt_low' in record:
            m['Rt_low'] = record['Rt_low']
        if 'Rt_up' in record:
            m['Rt_up'] = record['Rt_up']
        if 'population' in record:
            m['Rt_population'] = record['population']

def process(force=False):
    """Download and process the data"""
    store(download(force))

if __name__ == "__main__":
    process(force=True)
    dateCache.cacheReport()
