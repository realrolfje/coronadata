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
import re
import numpy as np
from dateutil import parser
from scipy.ndimage.filters import uniform_filter1d
from scipy.signal import savgol_filter
from statistics import mean

def readjson(filename):
    print('Reading '+filename)
    with open(filename, 'r') as json_file:
        return json.load(json_file)

def writejson(filename, adict):
    print('Writing '+filename)
    with open(filename, 'w') as file:
        file.write(json.dumps(adict))

# Turns US 10,000.00 into EU 10.000,00
def decimalstring(number):
    return "{:,}".format(number).replace(',','x').replace('.',',').replace('x','.')

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
        '../cache/NICE-intake-cumulative.json',
        'https://www.stichting-nice.nl/covid-19/public/intake-cumulative/'
    ) or freshdata

    freshdata = downloadIfStale(
        '../cache/NICE-intake-count.json',
        'https://www.stichting-nice.nl/covid-19/public/intake-count/'
    ) or freshdata
    
    freshdata = downloadIfStale(
        '../cache/NICE-zkh-intake-count.json',
        'https://www.stichting-nice.nl//covid-19/public/zkh/intake-count/'
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
        '../cache/rijskoverheid-coronadashboard-NL.json',
        'https://coronadashboard.rijksoverheid.nl/json/NL.json'
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
            'RNA' : {
                'totaal_RNA_per_ml'    : 0,
                'totaal_RNA_metingen'  : 0,
                'RNA_per_ml_avg'       : 0,
                'besmettelijk'         : None, # Aantal besmettelijke mensen op basis van RNA_avg
                'besmettelijk_error'   : None,
                'regio' : {
                    # This will contain data per veiligheidsregio:
                    # 'VR01' : {
                    #     'totaal_RNA_per_ml'    : 0,
                    #     'totaal_RNA_metingen'  : 0,
                    #     'RNA_per_ml_avg'       : 0,
                    #     'inwoners'             : 0,
                    #     'oppervlakte'          : 0                   
                    # }
                }
            },
            'rivm_totaal_tests'    : None,
            'rivm_aantal_testlabs' : None,
            'rivm_schatting_besmettelijk' : {
                'min'   : None, # Minimaal personen besmettelijk
                'value' : None, # Geschat personen besmettelijk
                'max'   : None  # Maximaal personen besmettelijk
            },
            'besmettingleeftijd_gemiddeld' : None,
            'besmettingleeftijd'   : {
                # key = leeftijdscategorie
                # value = aantal besmettingen
            }
        }    

# Not used yet, maybe handy to graph more stuff based on a single json
def builddaily():
    metenisweten = {}
    testpunten = {}

    print('Transform per-case data to daily totals')
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


    print("Add intensive care data")
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

    print("Add R numbers")
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

    print("Load veiligheidsregios for addign to sewage data")
    filename = '../data/veiligheidsregios.json'
    with open(filename, 'r') as json_file:
        veiligheidsregios = json.load(json_file)

    print("Add RNA sewege data per region")
    filename = '../cache/COVID-19_rioolwaterdata.json' 
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
        for record in data:

            # Fix rioolwaterdate. Non-ISO date 01-02-2020 will become ISO date 2020-02-01
            stringdate = record['Date_measurement']
            if re.search('-\d{4}$',stringdate):
                stringdate = datetime.datetime.strptime(stringdate,"%d-%m-%Y").strftime("%Y-%m-%d")

            if not isvaliddate(stringdate, filename):
                continue

            initrecord(stringdate, metenisweten)
            metenisweten[stringdate]['RNA']['totaal_RNA_per_ml'] += record['RNA_per_ml'] 
            metenisweten[stringdate]['RNA']['totaal_RNA_metingen'] += 1 
            metenisweten[stringdate]['RNA']['RNA_per_ml_avg'] = metenisweten[stringdate]['RNA']['totaal_RNA_per_ml'] / metenisweten[stringdate]['RNA']['totaal_RNA_metingen']

            regiocode = record['Security_region_code']
            if regiocode not in metenisweten[stringdate]['RNA']:
                metenisweten[stringdate]['RNA']['regio'][regiocode] = {
                    'totaal_RNA_per_ml'    : 0,
                    'totaal_RNA_metingen'  : 0,
                    'RNA_per_ml_avg'       : 0,
                    'inwoners'             : veiligheidsregios[regiocode]['inwoners'],
                    'oppervlak'            : veiligheidsregios[regiocode]['oppervlak']                   
                }
            metenisweten[stringdate]['RNA']['regio'][regiocode]['totaal_RNA_per_ml'] += record['RNA_per_ml'] 
            metenisweten[stringdate]['RNA']['regio'][regiocode]['totaal_RNA_metingen'] += 1 
            metenisweten[stringdate]['RNA']['regio'][regiocode]['RNA_per_ml_avg'] = metenisweten[stringdate]['RNA']['regio'][regiocode]['totaal_RNA_per_ml'] / metenisweten[stringdate]['RNA']['regio'][regiocode]['totaal_RNA_metingen']

    print("Add estimated ill based on CoronawatchNL data")
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

    print("Add total tests")
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

    print("Calculate average number of ill people based on Rna measurements")
    dates = []
    rna = []
    rna_error = []
    rivmschattingratio = []
    for date in metenisweten:
        gewogenrna = 0
        inwoners = 0

        # TODO: Checken of dit ook goed gaat met meerdere RWZI's in de regio die dan vermenigvuldigd
        # worden met de inwoners (= groter aandeel)
        for regio in metenisweten[date]['RNA']['regio']:
            regiodata = metenisweten[date]['RNA']['regio'][regio]
            gewogenrna += (regiodata['RNA_per_ml_avg'] * regiodata['inwoners'])
            inwoners += regiodata['inwoners']

        # Store measurement error
        metenisweten[date]['RNA']['besmettelijk_error'] = 1 - (inwoners / 17500000)

        if inwoners < 1000000:
            print('less than 1 million people covered by RNA data on '+date+": "+str(inwoners))

        # Choose nice cutover point where RIVM and RNA estimates cross/match on may 30
        # if parser.parse(date).date() > parser.parse('2020-05-30').date() and (parser.parse(date).date() <= (datetime.date.today() - datetime.timedelta(days=14)) or inwoners > 100000):
        if parser.parse(date).date() > parser.parse('2020-05-30').date() and (parser.parse(date).date() <= (datetime.date.today() - datetime.timedelta(days=5))):
            dates.append(date)
            rna.append(gewogenrna)
            rna_error.append(1 - (inwoners / 17500000))

    # https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter
    def double_savgol(inputArray):
        outputArray = savgol_filter(inputArray, 13, 1)
        outputArray = savgol_filter(outputArray, 13, 1)
        return outputArray

    # Smooth
    rna_avg = double_savgol(rna)
    rna_error = double_savgol(rna_error)

    # Compare to RIVM estimates and correct scale
    for idx, date in enumerate(dates):
        if metenisweten[date]['rivm_schatting_besmettelijk']['value'] and rna_avg[idx] > 1000:
           rivmschattingratio.append(metenisweten[date]['rivm_schatting_besmettelijk']['value']/rna_avg[idx])
    averageratio = mean(rivmschattingratio)
    print(averageratio)
    rna_avg = [x * averageratio for x in rna_avg]

    for i in range(len(dates)):
        date = dates[i]
        metenisweten[date]['RNA']['besmettelijk'] = rna_avg[i]
        metenisweten[date]['RNA']['besmettelijk_error'] = rna_error[i]

    print("Calculate average age of positive tested people")
    for datum in metenisweten:
        positief = 0
        som = 0
        for age in metenisweten[datum]['besmettingleeftijd']:
            som += metenisweten[datum]['besmettingleeftijd'][age] * int(age)
            positief += metenisweten[datum]['besmettingleeftijd'][age]

        if positief > 0:
            gemiddeld = som/positief
            metenisweten[datum]['besmettingleeftijd_gemiddeld'] = gemiddeld

    print("Calculate totals")
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