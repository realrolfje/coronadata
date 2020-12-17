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
from operator import itemgetter


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
    if number == round(number) and len(str(number)) <= 4:
        return str(number)
    else:
        return "{:,}".format(number).replace(',','x').replace('.',',').replace('x','.')

def switchdecimals(numberstring):
    return numberstring.replace(',','x').replace('.',',').replace('x','.')

def isnewer(file1, file2):
    return os.path.isfile(file1) and os.path.isfile(file2) and os.stat(file1).st_mtime > os.stat(file2).st_mtime 

def sortDictOnKey(dictionary):
    return dict(sorted(dictionary.items(), key=itemgetter(0)))

def downloadIfStale(filename, url):
    if os.path.isfile(filename) and os.stat(filename).st_mtime > ( time.time() - 3600):
        # print(filename+" exists.")
        return False
    else:
        print("Downloading fresh data to "+filename)
        urllib.request.urlretrieve(url, filename)
        return True

def downloadMostRecentAppleMobilityReport(filename):
    if os.path.isfile(filename) and os.stat(filename).st_mtime > ( time.time() - 3600):
        # print(filename+" exists.")
        return False
    else:
        print("Downloading fresh data to "+filename)
        for i in range(14):
            theday  = (datetime.date.today() - datetime.timedelta(days = i)).strftime("%Y-%m-%d")
            url = 'https://covid19-static.cdn-apple.com/covid19-mobility-data/2022HotfixDev27/v3/en-us/applemobilitytrends-'+theday+'.csv'
            try:
                print("Trying "+url, end="...")
                urllib.request.urlretrieve(url, filename)
                print("done.")
                return True
            except (urllib.error.HTTPError, urllib.error.HTTPError) as err:
                print("Error "+str(err))
        raise Exception("Sorry, no Apple mobility data found. Check https://covid19.apple.com/mobility") 

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

    freshdata = downloadIfStale(
        '../cache/lcps-covid-19.csv',
        'https://lcps.nu/wp-content/uploads/covid-19.csv'
    ) or freshdata

    # freshdata = downloadIfStale(
    #     '../cache/Google_Global_Mobility_Report.csv',
    #     'https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv'
    # ) or freshdata

    freshdata = downloadMostRecentAppleMobilityReport(
        '../cache/Apple_Global_Mobility_Report.csv'
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
            'nu_op_ic_lcps'        : None,
            'nu_op_ic_noncovid_lcps':None,
            'geweest_op_ic'        : 0,
            'opgenomen'            : 0,
            'nu_opgenomen'         : 0,
            'nu_opgenomen_lcps'    : None,
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
                'populatie_dekking'    : None,
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
            'rivm_totaal_personen_getest'      : None,
            'rivm_totaal_personen_positief'    : None,
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
            },
            'mobiliteit' : {
                'lopen' : None,
                'ov' : None,
                'rijden' : None
            }
        }    

# https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter
def smooth(inputArray):
    return double_savgol(inputArray, 2, 13, 1)

# https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter
def double_savgol(inputArray, iterations, window, order):
    outputArray = inputArray
    while iterations > 0:
        outputArray = savgol_filter(outputArray, window, order)
        iterations = iterations - 1
    return outputArray

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

    print("Add RNA sewage data per region")
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

            if 'RNA_per_ml' in record and record['RNA_per_ml']:
                rnavalue = record['RNA_per_ml']
            elif 'RNA_flow_per_100.000' in record and record['RNA_flow_per_100.000']:
                rnavalue = record['RNA_flow_per_100.000'] / 24650163389
            elif 'RNA_flow_per_100000' in record and record['RNA_flow_per_100000']:
                rnavalue = record['RNA_flow_per_100000'] / 24650163389
            else:
                continue

            # Ignore stations which measure less than 80% of their value from one region
            if float(switchdecimals(record['Percentage_in_security_region'])) < 0.8:
                continue

            initrecord(stringdate, metenisweten)
            metenisweten[stringdate]['RNA']['totaal_RNA_per_ml'] += rnavalue
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
            metenisweten[stringdate]['RNA']['regio'][regiocode]['totaal_RNA_per_ml'] += rnavalue
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
                #Jaar,Week,BeginDatum,EindDatum,Bron,AantalLaboratoria,Type,Aantal

                #Jaar,Week,BeginDatum,EindDatum,AantalLaboratoria,Type,Aantal
                year = row[0]
                week = row[1]
                startdatum = row[2]
                einddatum = row[3]
                bron = row[4]
                aantal_labs = row[5]
                valtype = row[6]
                aantal = int(row[7])

                if not isvaliddate(startdatum, filename):
                    continue

                if not isvaliddate(einddatum, filename):
                    continue

                if valtype == 'Totaal':
                    for n in range(int ((parser.parse(einddatum) - parser.parse(startdatum)).days)+1):
                        weekdatum = parser.parse(startdatum) + datetime.timedelta(n)
                        weekdatumstr = weekdatum.strftime("%Y-%m-%d")
                        initrecord(weekdatumstr, metenisweten)
                        metenisweten[weekdatumstr]['rivm_totaal_personen_getest'] = aantal/7
                        metenisweten[weekdatumstr]['rivm_aantal_testlabs'] = aantal_labs

                        # print(weekdatumstr+' '+str(aantal)+' /7= '+str(metenisweten[weekdatumstr]['rivm_totaal_personen_getest'])+' totaal personen getest per dag.')

                if valtype == 'Positief':
                    for n in range(int ((parser.parse(einddatum) - parser.parse(startdatum)).days)+1):
                        weekdatum = parser.parse(startdatum) + datetime.timedelta(n)
                        weekdatumstr = weekdatum.strftime("%Y-%m-%d")
                        initrecord(weekdatumstr, metenisweten)
                        metenisweten[weekdatumstr]['rivm_totaal_personen_positief'] = aantal/7

            line_count += 1

    print("Load LCPS data...")
    filename ='../cache/lcps-covid-19.csv'
    with open(filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:        
            if line_count > 0:
                #Datum,IC_Bedden_COVID,IC_Bedden_Non_COVID,Kliniek_Bedden,IC_Nieuwe_Opnames_COVID,Kliniek_Nieuwe_Opnames_COVID
                datum = datetime.datetime.strptime(row[0],"%d-%m-%Y").strftime("%Y-%m-%d")
                ic_bedden_covid = row[1]
                ic_bedden_non_covid = row[2]
                kliniek_bedden = row[3]
                ic_nieuwe_opnames = row[4]
                kliniek_nieuwe_opnames = row[5]

                # print("LCPS bedden " + datum + " " + ic_bedden_covid + " " + kliniek_bedden)

                initrecord(datum, metenisweten)
                metenisweten[datum]['nu_op_ic_lcps'] = int(ic_bedden_covid)
                metenisweten[datum]['nu_op_ic_noncovid_lcps'] = int(ic_bedden_non_covid)
                metenisweten[datum]['nu_opgenomen_lcps'] = int(kliniek_bedden)
            line_count = line_count + 1

    print("Load Apple Mobility Data")
    filename ='../cache/Apple_Global_Mobility_Report.csv'
    with open(filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        translate = {'walking': 'lopen', 'transit': 'OV', 'driving': 'rijden'}
        for row in csv_reader:
            if line_count == 0:
                headers = row
            elif row[0] == 'country/region' and row[1] == 'Netherlands':
                for idx,datum in enumerate(headers[6:]):                
                    vervoertype = translate[row[2]]
                    percentagestr = row[idx+6]
                    if percentagestr:
                        initrecord(datum, metenisweten)
                        metenisweten[datum]['mobiliteit'][vervoertype] = float(percentagestr)
            line_count = line_count + 1

    print("Calculate average number of ill people based on Rna measurements")
    dates = []
    rna = []
    rna_error = []
    rivmschattingratio = []

    # Record the newest date with more than 30 RNA measurements, which
    # is the last date we will use for estimates.
    for date in metenisweten:
        # Record last valid RNA date
        # print('RNA metingen '+date+' '+str(metenisweten[date]['RNA']['totaal_RNA_metingen']))
        if metenisweten[date]['RNA']['totaal_RNA_metingen'] > 30:
            lastrnadate = date

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
        metenisweten[date]['RNA']['populatie_dekking'] = inwoners / 17500000
        metenisweten[date]['RNA']['besmettelijk_error'] = 1 - (inwoners / 17500000)

        # if inwoners < 1000000:
        #     print('less than 1 million people covered by RNA data on '+date+": "+str(inwoners))

        # Choose nice cutover point where RIVM and RNA estimates cross/match on may 30
        # Also don't use too recent RNA data
        if parser.parse(date).date() > parser.parse('2020-05-30').date() and (parser.parse(date).date() <= parser.parse(lastrnadate).date()):
            dates.append(date)
            rna.append(gewogenrna)
            rna_error.append(1 - (inwoners / 17500000))

    # Smooth
    rna_avg = double_savgol(rna, 2, 13, 1)
    rna_error = double_savgol(rna_error, 2, 13, 1)

    # Compare to RIVM estimates and correct scale
    for idx, date in enumerate(dates):
        rivmschatting = metenisweten[date]['rivm_schatting_besmettelijk']['value']
        if rivmschatting and rivmschatting > 5000 and rna_avg[idx] > 1000:
           rivmschattingratio.append(rivmschatting/rna_avg[idx])
    averageratio = mean(rivmschattingratio)
    print("Average ratio between RIVM estimates and RNA data: " + str(round(averageratio,5)))
    rna_avg = [x * averageratio for x in rna_avg]

    for i in range(len(dates)):
        date = dates[i]
        metenisweten[date]['RNA']['besmettelijk'] = max(1,rna_avg[i]) # Don't allow negative or 0 numbers
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

    # Write sorted data
    writejson('../cache/daily-stats.json',  sortDictOnKey(metenisweten))
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