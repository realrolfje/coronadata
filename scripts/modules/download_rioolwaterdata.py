#!/usr/bin/env python3
#
# Downloads rioolwaterdata
# https://data.rivm.nl/geonetwork/srv/dut/catalog.search#/metadata/a2960b68-9d3f-4dc3-9485-600570cd52b9
#

import os
from utilities import downloadIfStale, readjson
from defaults import cachedir
from metenisweten import initrecord
from datecache import dateCache
import re
import datetime


def download(force=False) -> str:
    filename = os.path.join(cachedir, "COVID-19_rioolwaterdata.json")
    if downloadIfStale(
        filename=filename,
        url="https://data.rivm.nl/covid-19/COVID-19_rioolwaterdata.json",
        force = force):
        return filename
    else:
        return None


def store(downloaded_file) -> bool:
    if downloaded_file == None:
        return False

    print("Add RNA sewage data per region")
    data = readjson(downloaded_file)
    cachedDate = None
    for record in data:
        if cachedDate != record['Date_measurement']:
            cachedDate = record['Date_measurement']

            # Fix rioolwaterdate. Non-ISO date 01-02-2020 will become ISO date 2020-02-01
            stringdate = dateCache.sanitizeDate(record['Date_measurement'])
            if not dateCache.isvaliddate(stringdate, downloaded_file):
                stringdate = None

        if stringdate == None:
            continue

        if record.get('RNA_flow_per_100000') != None:
            rnavalue = int(record['RNA_flow_per_100000'])
            # print(str(rnavalue), end=",")
        else:
            # print("No RNA Flow data in %s (%s) for date %s." % (record['RWZI_AWZI_name'],record['RWZI_AWZI_code'],stringdate))
            continue

        m = initrecord(stringdate)
        m['RNA']['totaal_RNA_per_100k'] += rnavalue
        m['RNA']['totaal_RNA_metingen'] += 1
        m['RNA']['RNA_per_100k_avg'] = m['RNA']['totaal_RNA_per_100k'] / \
            m['RNA']['totaal_RNA_metingen']

        # regiocode = record['Security_region_code']
        # if regiocode not in m['RNA']:
        #     m['RNA']['regio'][regiocode] = {
        #         'totaal_RNA_per_100k'    : 0,
        #         'totaal_RNA_metingen'  : 0,
        #         'RNA_per_100k_avg'       : 0,
        #         'inwoners'             : veiligheidsregios[regiocode]['inwoners'],
        #         'oppervlak'            : veiligheidsregios[regiocode]['oppervlak']
        #     }
        # m['RNA']['regio'][regiocode]['totaal_RNA_per_100k'] += rnavalue
        # m['RNA']['regio'][regiocode]['totaal_RNA_metingen'] += 1
        # m['RNA']['regio'][regiocode]['RNA_per_100k_avg'] = metenisweten[stringdate]['RNA']['regio'][regiocode]['totaal_RNA_per_100k'] / metenisweten[stringdate]['RNA']['regio'][regiocode]['totaal_RNA_metingen']

    return True

def process(force=False):
    """Download and process the data"""
    store(download(force))

if __name__ == "__main__":
    process(force=True)
    dateCache.cacheReport()
