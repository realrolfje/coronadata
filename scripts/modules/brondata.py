#!/usr/bin/env python3
#
# Haalt COVID-19 testresultaten op bij RIVM en NICE
#
#

import urllib.request
import os.path
import time
import json

def readjson(filename):
    print('Reading '+filename)
    with open(filename, 'r') as json_file:
        return json.load(json_file)

def writejson(filename, adict):
    print('Writing '+filename)
    with open(filename, 'w') as file:
        file.write(json.dumps(adict))

def downloadIfStale(filename, url):
    if os.path.isfile(filename) and os.stat(filename).st_mtime > ( time.time() - 3600):
        # print(filename+" exists.")
        return False
    else:
        print("Downloading fresh data to "+filename)
        urllib.request.urlretrieve(url, filename)
        return True

def download():
    freshdata = False

    freshdata = downloadIfStale(
        '../cache/COVID-19_casus_landelijk.json',
        'https://data.rivm.nl/covid-19/COVID-19_casus_landelijk.json'
    ) or freshdata

    freshdata = downloadIfStale(
        '../cache/NICE-intake-cumulative.json',
        'https://www.stichting-nice.nl/covid-19/public/intake-cumulative/'
    ) or freshdata

    freshdata = downloadIfStale(
        '../cache/NICE-intake-count.json',
        'https://www.stichting-nice.nl/covid-19/public/intake-count/'
    ) or freshdata
    
    # https://data.rivm.nl/geonetwork/srv/dut/catalog.search#/metadata/ed0699d1-c9d5-4436-8517-27eb993eab6e?tab=relations
    freshdata = downloadIfStale(
        '../cache/COVID-19_reproductiegetal.json',
        'https://data.rivm.nl/covid-19/COVID-19_reproductiegetal.json'
    ) or freshdata

    # https://data.rivm.nl/geonetwork/srv/dut/catalog.search#/metadata/a2960b68-9d3f-4dc3-9485-600570cd52b9
    freshdata = downloadIfStale(
        '../cache/COVID-19_rioolwaterdata.json',
        'https://data.rivm.nl/covid-19/COVID-19_rioolwaterdata.json'
    ) or freshdata

    return freshdata

def initrecord(date, metenisweten):
    if (date not in metenisweten):
        metenisweten[date] = {
            'positief'            : 0,
            'totaal_positief'     : 0,
            'nu_op_ic'            : 0,
            'geweest_op_ic'       : 0,
            'opgenomen'           : 0,
            'totaal_opgenomen'    : 0,
            'overleden'           : 0,
            'totaal_overleden'    : 0,
            'rivm-datum'          : None,
            'Rt_avg'              : None,
            'Rt_low'              : None,
            'Rt_up'               : None,
            'Rt_population'       : None,
            'totaal_RNA_per_ml'   : 0,
            'totaal_RNA_metingen' : 0,
            'RNA_per_ml_avg'      : 0
        }    

# Not used yet, maybe handy to graph more stuff based on a single json
def builddaily():
    metenisweten = {}
    testpunten = {}

    with open('../cache/COVID-19_casus_landelijk.json', 'r') as json_file:
        data = json.load(json_file)
        for record in data:
            initrecord(record['Date_statistics'], metenisweten)
            metenisweten[record['Date_statistics']]['positief'] += 1

            if (record['Hospital_admission'] == "Yes"):
                metenisweten[record['Date_statistics']]['opgenomen'] += 1

            # metenisweten[record['Date_statistics']] = record['Agegroup']
            metenisweten[record['Date_statistics']]['rivm-datum'] = record['Date_file']

            if (record['Deceased'] == 'Yes'):
                metenisweten[record['Date_statistics']]['overleden'] += 1

            testpunt = record['Municipal_health_service']
            if testpunt not in testpunten:
                testpunten[testpunt] = 1
            else:
                testpunten[testpunt] += 1


    with open('../cache/NICE-intake-count.json', 'r') as json_file:
        data = json.load(json_file)
        for record in data:
            initrecord(record['date'], metenisweten)
            metenisweten[record['date']]['nu_op_ic'] += record['value']

    with open('../cache/NICE-intake-cumulative.json', 'r') as json_file:
        data = json.load(json_file)
        for record in data:
            initrecord(record['date'], metenisweten)
            metenisweten[record['date']]['geweest_op_ic'] += record['value']

    with open('../cache/COVID-19_reproductiegetal.json') as json_file:
        data = json.load(json_file)
        for record in data:
            initrecord(record['Date'], metenisweten)
            if 'Rt_avg' in record:
                metenisweten[record['Date']]['Rt_avg'] = record['Rt_avg']
            if 'Rt_low' in record:
                metenisweten[record['Date']]['Rt_low'] = record['Rt_low']
            if 'Rt_up' in record:
                metenisweten[record['Date']]['Rt_up']  = record['Rt_up']
            if 'population' in record:
                metenisweten[record['Date']]['Rt_population']  = record['population']

    with open('../cache/COVID-19_rioolwaterdata.json') as json_file:
        data = json.load(json_file)
        for record in data:
            initrecord(record['Date_measurement'], metenisweten)
            metenisweten[record['Date_measurement']]['totaal_RNA_per_ml'] += record['RNA_per_ml'] 
            metenisweten[record['Date_measurement']]['totaal_RNA_metingen'] += 1 
            metenisweten[record['Date_measurement']]['RNA_per_ml_avg'] = metenisweten[record['Date_measurement']]['totaal_RNA_per_ml'] / metenisweten[record['Date_measurement']]['totaal_RNA_metingen'] 

    totaal_positief = 0
    totaal_opgenomen = 0
    totaal_overleden = 0
    for datum in metenisweten:
        totaal_positief  += metenisweten[datum]['positief']
        totaal_opgenomen += metenisweten[datum]['opgenomen']
        totaal_overleden += metenisweten[datum]['overleden']

        metenisweten[datum]['totaal_positief'] = totaal_positief
        metenisweten[datum]['totaal_opgenomen'] = totaal_opgenomen
        metenisweten[datum]['totaal_overleden'] = totaal_overleden

    writejson('../cache/daily-stats.json', metenisweten)
    writejson('../cache/testlocaties.json', testpunten)

def freshdata():
    if download():
        builddaily()

if __name__ == "__main__":
    freshdata()