#!/usr/bin/env python3
#
# Haalt COVID-19 testresultaten op bij RIVM en NICE
#
#

import urllib.request
import os.path
import datetime
import time
import json
import csv
from dateutil import parser
from scipy.ndimage.filters import uniform_filter1d

def readjson(filename):
    print('Reading '+filename)
    with open(filename, 'r') as json_file:
        return json.load(json_file)

def writejson(filename, adict):
    print('Writing '+filename)
    with open(filename, 'w') as file:
        file.write(json.dumps(adict))

def isnewer(file1, file2):
    return os.path.isfile(file1) and os.path.isfile(file2) and os.stat(file1).st_mtime > os.stat(file2).st_mtime 

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

    freshdata = downloadIfStale(
        '../cache/J535D165-RIVM_NL_contagious_estimate.csv',
        'https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data-dashboard/data-contagious/RIVM_NL_contagious_estimate.csv'
    ) or freshdata

    freshdata = downloadIfStale(
        '../cache/J535D165-RIVM_NL_contagious_estimate.csv',
        'https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data-dashboard/data-contagious/RIVM_NL_contagious_estimate.csv'
    ) or freshdata

    freshdata = downloadIfStale(
        '../cache/J535D165-RIVM_NL_test_latest.csv',
        'https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data-misc/data-test/RIVM_NL_test_latest.csv'
    ) or freshdata

    freshdata = downloadIfStale(
        '../cache/NICE-zkh-intake-count.json',
        'https://www.stichting-nice.nl//covid-19/public/zkh/intake-count/'
    ) or freshdata

    return freshdata

def isvaliddate(datestring, filename):
    parseddate = parser.parse(datestring).date()
    if parseddate >= datetime.date.fromisoformat('2020-01-01') and parseddate <= datetime.date.today():
        return True
    elif filename:
        print('Ignoring invalid date '+datestring+' in '+filename+'.')
    return False


def initrecord(date, metenisweten):
    if (date not in metenisweten):
        metenisweten[date] = {
            'positief'             : 0,
            'totaal_positief'      : 0,
            'nu_op_ic'             : 0,
            'geweest_op_ic'        : 0,
            'opgenomen'            : 0,
            'nu_opgenomen'         : 0,
            'totaal_opgenomen'     : 0,
            'overleden'            : 0,
            'totaal_overleden'     : 0,
            'rivm-datum'           : None,
            'Rt_avg'               : None,
            'Rt_low'               : None,
            'Rt_up'                : None,
            'Rt_population'        : None,
            'totaal_RNA_per_ml'    : 0,
            'totaal_RNA_metingen'  : 0,
            'RNA_per_ml_avg'       : 0,
            'besmettelijk_obv_rna' : None, # Aantal besmettelijke mensen op basis van RNA_avg
            'rivm_totaal_tests'    : None,
            'rivm_aantal_testlabs' : None,
            'rivm_schatting_besmettelijk' : {
                'min'   : None, # Minimaal personen besmettelijk
                'value' : None, # Geschat personen besmettelijk
                'max'   : None  # Maximaal personen besmettelijk
            },
            'besmettingleeftijd'   : {
                # key = leeftijdscategorie
                # value = aantal besmettingen
            }
        }    

# Not used yet, maybe handy to graph more stuff based on a single json
def builddaily():
    metenisweten = {}
    testpunten = {}

    # Transform per-case data to daily totals
    filename = '../cache/COVID-19_casus_landelijk.json'
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
        for record in data:
            if not isvaliddate(record['Date_statistics'], filename):
                continue

            initrecord(record['Date_statistics'], metenisweten)
            metenisweten[record['Date_statistics']]['positief'] += 1

            if (record['Hospital_admission'] == "Yes"):
                metenisweten[record['Date_statistics']]['opgenomen'] += 1

            # metenisweten[record['Date_statistics']] = record['Agegroup']
            metenisweten[record['Date_statistics']]['rivm-datum'] = record['Date_file']

            if (record['Deceased'] == 'Yes'):
                metenisweten[record['Date_statistics']]['overleden'] += 1

            try:
                # Age groups are 0-10, 10-20, 30-40 etc, we make that 5, 15, 25, 35.
                age = int(record['Agegroup'].split('-')[0].split('+')[0])+5
                if age not in metenisweten[record['Date_statistics']]['besmettingleeftijd']:
                    metenisweten[record['Date_statistics']]['besmettingleeftijd'][age] = 1
                else: 
                    metenisweten[record['Date_statistics']]['besmettingleeftijd'][age] += 1
            except ValueError:
                # print('ERROR '+record['Date_statistics'] + ' | ' + record['Agegroup'])
                pass

            testpunt = record['Municipal_health_service']
            if testpunt not in testpunten:
                testpunten[testpunt] = 1
            else:
                testpunten[testpunt] += 1


    # Add intensive care data
    filename = '../cache/NICE-intake-count.json' 
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
        for record in data:
            if not isvaliddate(record['date'], filename):
                continue
            initrecord(record['date'], metenisweten)
            metenisweten[record['date']]['nu_op_ic'] += record['value']

    filename = '../cache/NICE-intake-cumulative.json'
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
        for record in data:
            if not isvaliddate(record['date'], filename):
                continue
            initrecord(record['date'], metenisweten)
            metenisweten[record['date']]['geweest_op_ic'] += record['value']

    filename = '../cache/NICE-zkh-intake-count.json'
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
        for record in data:
            if not isvaliddate(record['date'], filename):
                continue
            initrecord(record['date'], metenisweten)
            metenisweten[record['date']]['nu_opgenomen'] += record['value']

    # Add R numbers
    filename = '../cache/COVID-19_reproductiegetal.json' 
    with open(filename , 'r') as json_file:
        data = json.load(json_file)
        for record in data:
            if not isvaliddate(record['Date'], filename):
                continue
            initrecord(record['Date'], metenisweten)
            if 'Rt_avg' in record:
                metenisweten[record['Date']]['Rt_avg'] = record['Rt_avg']
            if 'Rt_low' in record:
                metenisweten[record['Date']]['Rt_low'] = record['Rt_low']
            if 'Rt_up' in record:
                metenisweten[record['Date']]['Rt_up']  = record['Rt_up']
            if 'population' in record:
                metenisweten[record['Date']]['Rt_population']  = record['population']

    # Add RNA sewege data
    filename = '../cache/COVID-19_rioolwaterdata.json' 
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
        for record in data:

            # Fix rioolwaterdate.
            stringdate = record['Date_measurement']
            if stringdate.endswith('-2020'):
                stringdate = datetime.datetime.strptime(stringdate,"%d-%m-%Y").strftime("%Y-%m-%d")

            if not isvaliddate(stringdate, filename):
                continue

            initrecord(stringdate, metenisweten)
            metenisweten[stringdate]['totaal_RNA_per_ml'] += record['RNA_per_ml'] 
            metenisweten[stringdate]['totaal_RNA_metingen'] += 1 
            metenisweten[stringdate]['RNA_per_ml_avg'] = metenisweten[stringdate]['totaal_RNA_per_ml'] / metenisweten[stringdate]['totaal_RNA_metingen']

    # Add estimated ill based on CoronawatchNL data
    filename = '../cache/J535D165-RIVM_NL_contagious_estimate.csv'
    with open(filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:        
            if line_count > 0:
                datum = row[0]
                metingtype = row[1]
                waarde = row[2]

                if not isvaliddate(datum, filename):
                    continue
                initrecord(datum, metenisweten)

                try:
                    if metingtype == 'Minimum':
                        metenisweten[datum]['rivm_schatting_besmettelijk']['min'] = int(waarde)
                    elif metingtype == 'Maximum':
                        metenisweten[datum]['rivm_schatting_besmettelijk']['max'] = int(waarde)
                    elif metingtype == 'Geschat aantal besmettelijke mensen':
                        metenisweten[datum]['rivm_schatting_besmettelijk']['value'] = int(waarde)
                    else:
                        print('onbekend metingtype in J535D165-RIVM_NL_contagious_estimate.csv: '+metingtype)
                except ValueError:
                    pass

            line_count += 1

    # Add total tests
    filename ='../cache/J535D165-RIVM_NL_test_latest.csv'
    with open(filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:        
            if line_count > 0:
                #Jaar,Week,BeginDatum,EindDatum,AantalLaboratoria,Type,Aantal
                year = row[0]
                week = row[1]
                startdatum = row[2]
                einddatum = row[3]
                aantal_labs = row[4]
                valtype = row[5]
                aantal = int(row[6])

                if not isvaliddate(startdatum, filename):
                    continue

                if not isvaliddate(einddatum, filename):
                    continue

                if valtype == 'Totaal':
                    for n in range(int ((parser.parse(einddatum) - parser.parse(startdatum)).days)+1):
                        weekdatum = parser.parse(startdatum) + datetime.timedelta(n)
                        weekdatumstr = weekdatum.strftime("%Y-%m-%d")
                        initrecord(weekdatumstr, metenisweten)
                        metenisweten[weekdatumstr]['rivm_totaal_tests'] = aantal/7
                        metenisweten[weekdatumstr]['rivm_aantal_testlabs'] = aantal_labs

            line_count += 1

    # Calculate average number of ill people based on Rna measurements
    dates = []
    rna = []
    for date in metenisweten:
        if metenisweten[date]['RNA_per_ml_avg']:
            dates.append(date)
            rna.append(metenisweten[date]['RNA_per_ml_avg'])
    rna_avg = [x*37 for x in uniform_filter1d(rna, size=20)]

    for i in range(len(dates)):
        date = dates[i]
        besmettelijk = rna_avg[i]
        metenisweten[date]['besmettelijk_obv_rna'] = besmettelijk

    # Calculate totals
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
    if download() or isnewer(__file__, '../cache/daily-stats.json'):
        builddaily()


def getDateRange(metenisweten):
    for datum in metenisweten:
        try:
            mindatum
        except NameError:
            mindatum = parser.parse(datum)

        try:
            maxdatum
        except NameError:
            maxdatum = parser.parse(datum)

        mindatum = min(mindatum, parser.parse(datum))
        maxdatum = max(maxdatum, parser.parse(datum))

    date_range = [mindatum + datetime.timedelta(days=x)
                  for x in range(0, (maxdatum-mindatum).days+7)]
    return date_range

if __name__ == "__main__":
    freshdata()