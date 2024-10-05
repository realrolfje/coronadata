#!/usr/bin/env python3

# Downloads the varianten dataset.
# See data.rivm.nl, Covid-19 reproductiegetal
# See https://data.rivm.nl/covid-19/
#
#
import os
from utilities import downloadIfStale, readjson
from defaults import cachedir
from metenisweten import initrecord
from datecache import dateCache


def download(force=False) -> str:
    filename = os.path.join(cachedir, "COVID-19_varianten.json")
    if downloadIfStale(
        filename=filename,
        url='https://data.rivm.nl/covid-19/COVID-19_varianten.json',
        force = force):
        return filename
    else:
        return None


def store(downloaded_file) -> bool:
    if downloaded_file == None:
        return False 

    data = readjson(downloaded_file)
    for record in data:
        datum = record['Date_of_statistics_week_start']
        m = initrecord(datum)
        if record['Variant_code'] not in m['varianten']:
            m['varianten'][record['Variant_code']] = {
                'name': record['Variant_name'],
                'ECDC_category': record['ECDC_category'],
                'WHO_category': record['WHO_category'],
                'includes_old_samples': record.get('May_include_samples_listed_before', False),
                'sample_size': record['Sample_size'],
                'cases': record['Variant_cases']
            }
        # if datum.startswith('2024'):
        #     print(f"{datum} {m['varianten'][record['Variant_code']]} {m['varianten'][record['Variant_code']]['sample_size']} {m['varianten'][record['Variant_code']]['cases']}")
    return True


def process(force=False):
    """Download and process the data"""
    store(download(force))

if __name__ == "__main__":
    process(force=True)
    dateCache.cacheReport()
