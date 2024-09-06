#!/usr/bin/env python3
#
# Haalt COVID-19 testresultaten op bij RIVM en NICE
#
#
# TODO:
# https://coronadashboard.government.nl/landelijk/varianten -> SVG format, need to find the source.
# https://www.zelftestgedaan.nl/self_tests.json -> unreliable source, too little data.
#

import urllib.request
from urllib.error import URLError, HTTPError
import os.path
import datetime
import time
import json
import csv
import re
from scipy.signal import savgol_filter
from statistics import mean
from operator import itemgetter
from math import log

from ./defaults import timezone
from datecache import dateCache
from utilities \
    import readjson, writejson, \
           downloadIfStale, downloadBinaryIfStale, \
           decimalstring, isnewer, switchdecimals, \
           logError
from metenisweten import metenisweten, initrecord, writeMetenIsWeten
from download_Rt import process as process_Rt
from download_Zkh import process as process_Zkh



def downloadMostRecentAppleMobilityReport(filename):
    if os.path.isfile(filename) and os.stat(filename).st_mtime > (time.time() - 3600):
        # print(filename+" exists.")
        return False
    else:
        print("Downloading fresh data to "+filename, end="...")
        url = 'https://covid19-static.cdn-apple.com/covid19-mobility-data/2210HotfixDev16/v3/en-us/applemobilitytrends-2022-03-26.csv'
        try:
            urllib.request.urlretrieve(url, filename)
            print("done")
            return True
        except (urllib.error.HTTPError, urllib.error.HTTPError) as err:
            print("Error downloding %s: %s" % (url, str(err)))

        raise Exception(
            "Sorry, no Apple mobility data found. Check https://covid19.apple.com/mobility")


def downloadECDCMap():
    logError("ECDC No longer generates a COVID indicator map")
    return

    url = "https://www.ecdc.europa.eu/en/covid-19/situation-updates/weekly-maps-coordinated-restriction-free-movement"
    with urllib.request.urlopen(url) as response:
        meta = response.headers
        charset = meta.get_content_charset() or 'utf-8'
        responsebody = response.read().decode(charset)
        imglink = re.findall(
            'https://www\.ecdc\.europa\.eu/.+/public/images/.*_CouncilMap\.png', responsebody)[0]
        print("Download ECDC map from: "+imglink)

        return downloadBinaryIfStale(
            '../docs/extern/ECDC_Subnational_Combined_traffic.png',
            imglink
        )


def download():
    freshdata = False

    markerfile = '../docs/extern/ECDC_Subnational_Combined_traffic.png'
    if os.path.isfile(markerfile):
        lastdownload = datetime.datetime.fromtimestamp(
            os.stat(markerfile).st_mtime, tz=timezone)
    else:
        lastdownload = datetime.datetime.fromtimestamp(0, tz=timezone)

    if lastdownload > (datetime.datetime.now(tz=timezone) - datetime.timedelta(minutes=20)):
        print("Downloaded ECDC map less than 20 minutes ago (%s), no new download." % lastdownload)
        return True

    freshdata = downloadECDCMap() or freshdata

    freshdata = downloadIfStale(
        '../cache/COVID-19_casus_landelijk.json',
        'https://data.rivm.nl/covid-19/COVID-19_casus_landelijk.json'
    ) or freshdata

    # freshdata = downloadIfStale(
    #     '../cache/COVID-19_ziekenhuisopnames.json',
    #     'https://data.rivm.nl/covid-19/COVID-19_ziekenhuisopnames.json'
    # ) or freshdata

    # https://data.rivm.nl/geonetwork/srv/dut/catalog.search#/metadata/a2960b68-9d3f-4dc3-9485-600570cd52b9
    freshdata = downloadIfStale(
        '../cache/COVID-19_rioolwaterdata.json',
        'https://data.rivm.nl/covid-19/COVID-19_rioolwaterdata.json'
    ) or freshdata


    freshdata = downloadIfStale(
        '../cache/COVID-19_prevalentie.json',
        'https://data.rivm.nl/covid-19/COVID-19_prevalentie.json'
    ) or freshdata

    # Uitgevoerde tests van VOOR 2021, per week
    freshdata = downloadIfStale(
        '../cache/J535D165-RIVM_NL_test_latest.csv',
        'https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data-misc/data-test/RIVM_NL_test_latest.csv'
    ) or freshdata

    # Uitgevoerde tests in 2021, per dag van RIVM
    freshdata = downloadIfStale(
        '../cache/COVID-19_uitgevoerde_testen.json',
        'https://data.rivm.nl/covid-19/COVID-19_uitgevoerde_testen.json'
    ) or freshdata

    freshdata = downloadIfStale(
        '../cache/rijksoverheid-coronadashboard-NL.json',
        'https://coronadashboard.rijksoverheid.nl/json/NL.json'
    ) or freshdata

    freshdata = downloadIfStale(
        '../cache/lcps-covid-19.csv',
        'https://lcps.nu/wp-content/uploads/covid-19.csv'
    ) or freshdata

    freshdata = downloadIfStale(
        '../cache/COVID-19_Infectieradar_symptomen_per_dag.json',
        'https://data.rivm.nl/covid-19/COVID-19_Infectieradar_symptomen_per_dag.json'
    ) or freshdata

    freshdata = downloadIfStale(
        '../cache/COVID-19_varianten.json',
        'https://data.rivm.nl/covid-19/COVID-19_varianten.json'
    ) or freshdata

    freshdata = downloadIfStale(
        '../cache/COVID-19_vaccinatiegraad_per_gemeente_per_week_leeftijd.json',
        'https://data.rivm.nl/covid-19/COVID-19_vaccinatiegraad_per_gemeente_per_week_leeftijd.json'
    ) or freshdata

    # freshdata = downloadIfStale(
    #     '../cache/Google_Global_Mobility_Report.csv',
    #     'https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv'
    # ) or freshdata

    # freshdata = downloadMostRecentAppleMobilityReport(
    #     '../cache/Apple_Global_Mobility_Report.csv'
    # ) or freshdata

    return freshdata


def isvaliddate(datestring, filename):
    dateCache.isvaliddate(datestring, filename)


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


def intOrNone(input):
    try:
        return int(input)
    except TypeError:
        return None
    except ValueError:
        return None


def intOrZero(input):
    try:
        return int(input)
    except TypeError:
        return 0
    except ValueError:
        return 0


def builddaily():
    # Load previous version of the data, so that we always keep it all.
    testpunten = {}

    print('Transform per-case data to daily totals')
    filename = '../cache/COVID-19_casus_landelijk.json'
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
        print('Loaded %s, contains %s case records.' %
              (filename, decimalstring(len(data))))

        for record in data:
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

        print('Processed ' + decimalstring(len(metenisweten)) + ' records.')

    # print("Add hospitalization data")
    # filename = '../cache/NICE-intake-count.json'
    # with open(filename, 'r') as json_file:
    #     data = json.load(json_file)


    # print("Load veiligheidsregios for addign to sewage data")
    # filename = '../data/veiligheidsregios.json'
    # with open(filename, 'r') as json_file:
    #     veiligheidsregios = json.load(json_file)

    print("Add RNA sewage data per region")
    filename = '../cache/COVID-19_rioolwaterdata.json'
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
        cachedDate = None
        cachedDateValid = False
        for record in data:
            if cachedDate != record['Date_measurement']:
                cachedDate = record['Date_measurement']

                # Fix rioolwaterdate. Non-ISO date 01-02-2020 will become ISO date 2020-02-01
                stringdate = record['Date_measurement']
                if re.search('-\d{4}$', stringdate):
                    stringdate = datetime.datetime.strptime(
                        stringdate, "%d-%m-%Y").strftime("%Y-%m-%d")

                if not dateCache.isvaliddate(stringdate, filename):
                    cachedDateValid = False
                else:
                    cachedDateValid = True

            if not cachedDateValid:
                continue

            if 'RNA_flow_per_100000' in record and record['RNA_flow_per_100000']:
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

    print("Add estimated ill based on RIVM (prevalentie)")
    filename = '../cache/COVID-19_prevalentie.json'
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
        cachedDate = None
        cachedDateValid = False
        for record in data:
            stringdate = record['Date']
            if cachedDate != stringdate:
                cachedDate = stringdate

                if not dateCache.isvaliddate(stringdate, filename):
                    cachedDateValid = False
                else:
                    cachedDateValid = True

            if not cachedDateValid:
                continue

            try:
                metenisweten[stringdate]['rivm_schatting_besmettelijk']['min'] = int(
                    record['prev_low'])
                metenisweten[stringdate]['rivm_schatting_besmettelijk']['max'] = int(
                    record['prev_up'])
                metenisweten[stringdate]['rivm_schatting_besmettelijk']['value'] = int(
                    record['prev_avg'])
            except ValueError as e:
                print('Ignored: ', e)
                pass
            except KeyError as e:
                print('Ignored: ', e)
                pass

    print("Add infectieradar percentage met COVID-19 klachten")
    filename = '../cache/COVID-19_Infectieradar_symptomen_per_dag.json'
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
        cachedDate = None
        cachedDateValid = False
        for record in data:
            stringdate = record['Date_of_statistics']

            if cachedDate != stringdate:
                cachedDate = stringdate

                if not dateCache.isvaliddate(stringdate, filename):
                    cachedDateValid = False
                else:
                    cachedDateValid = True

            if not cachedDateValid:
                continue

            try:
                percentage = float(record['Perc_covid_symptoms'])
                metenisweten[stringdate]['rivm_infectieradar_perc'] = percentage
            except TypeError as e:
                print('Ignored: ', e)
                pass
            except ValueError as e:
                print('Ignored: ', e)
                pass
            except KeyError as e:
                print('Ignored: ', e)
                pass

    print("Add total tests (until 2020, weekbasis)")
    filename = '../cache/J535D165-RIVM_NL_test_latest.csv'
    with open(filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                # Jaar,Week,BeginDatum,EindDatum,Bron,AantalLaboratoria,Type,Aantal

                # Jaar,Week,BeginDatum,EindDatum,AantalLaboratoria,Type,Aantal
                year = row[0]
                week = row[1]
                startdatum = row[2]
                einddatum = row[3]
                bron = row[4]
                aantal_labs = row[5]
                valtype = row[6]
                aantal = int(row[7])

                if not dateCache.isvaliddate(startdatum, filename):
                    continue

                if not dateCache.isvaliddate(einddatum, filename):
                    continue

                if valtype == 'Totaal':
                    for n in range(int((dateCache.parse(einddatum) - dateCache.parse(startdatum)).days)+1):
                        weekdatum = dateCache.parse(
                            startdatum) + datetime.timedelta(n)
                        weekdatumstr = weekdatum.strftime("%Y-%m-%d")
                        m = initrecord(weekdatumstr)
                        m['rivm_totaal_personen_getest'] = aantal/7
                        m['rivm_aantal_testlabs'] = aantal_labs

                        # print(weekdatumstr+' '+str(aantal)+' /7= '+str(metenisweten[weekdatumstr]['rivm_totaal_personen_getest'])+' totaal personen getest per dag.')

                if valtype == 'Positief':
                    for n in range(int((dateCache.parse(einddatum) - dateCache.parse(startdatum)).days)+1):
                        weekdatum = dateCache.parse(
                            startdatum) + datetime.timedelta(n)
                        weekdatumstr = weekdatum.strftime("%Y-%m-%d")
                        m = initrecord(weekdatumstr)
                        m['rivm_totaal_personen_positief'] = aantal/7

            line_count += 1

    print("Add total tests (from start 2021, daily basis)")
    filename = '../cache/COVID-19_uitgevoerde_testen.json'
    with open(filename, 'r') as json_file:
        data = json.load(json_file)

        temp_totaltests = {}
        temp_positive = {}

        for record in data:
            # print(record)

            if record['Date_of_statistics'] not in temp_totaltests:
                temp_totaltests[record['Date_of_statistics']] = 0
            temp_totaltests[record['Date_of_statistics']] = temp_totaltests[record['Date_of_statistics']
                                                                            ] + intOrZero(record['Tested_with_result'])

            if record['Date_of_statistics'] not in temp_positive:
                temp_positive[record['Date_of_statistics']] = 0
            temp_positive[record['Date_of_statistics']
                          ] = temp_positive[record['Date_of_statistics']] + intOrZero(record['Tested_positive'])

        # Overwrite total number of tests
        for key in temp_totaltests:
            initrecord(key)['rivm_totaal_tests'] = temp_totaltests[key]

        # Overwrite total number of positivetests
        for key in temp_positive:
            initrecord(key)['rivm_totaal_tests_positief'] = temp_positive[key]

    print("Load LCPS data...")
    filename = '../cache/lcps-covid-19.csv'
    with open(filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                # Datum,IC_Bedden_COVID,IC_Bedden_Non_COVID,Kliniek_Bedden,IC_Nieuwe_Opnames_COVID,Kliniek_Nieuwe_Opnames_COVID
                datum = datetime.datetime.strptime(
                    row[0], "%d-%m-%Y").strftime("%Y-%m-%d")
                ic_bedden_covid = row[1]
                ic_bedden_non_covid = row[2]
                kliniek_bedden = row[3]
                ic_nieuwe_opnames = row[4]
                kliniek_nieuwe_opnames = row[5]

                # print("LCPS bedden " + datum + " " + ic_bedden_covid + " " + kliniek_bedden)

                m = initrecord(datum)
                m['nu_op_ic_lcps'] = intOrNone(ic_bedden_covid)
                m['nu_op_ic_noncovid_lcps'] = intOrNone(ic_bedden_non_covid)
                m['nu_opgenomen_lcps'] = intOrNone(kliniek_bedden)
            line_count = line_count + 1

    print("Load covid variant statistics")
    filename = '../cache/COVID-19_varianten.json'
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
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

    # print("Load vaccinatiegraad per leeftijd/gemeente")
    # filename = '../cache/COVID-19_vaccinatiegraad_per_gemeente_per_week_leeftijd.json'
    # with open(filename, 'r') as json_file:
    #     data = json.load(json_file)
    #     for record in data:
    #         datum = record['Date_of_statistics']
    #         initrecord(datum, metenisweten)

    # print("Load Apple Mobility Data")
    # filename ='../cache/Apple_Global_Mobility_Report.csv'
    # with open(filename, 'r') as csv_file:
    #     csv_reader = csv.reader(csv_file, delimiter=',')
    #     line_count = 0
    #     translate = {'walking': 'lopen', 'transit': 'OV', 'driving': 'rijden'}
    #     for row in csv_reader:
    #         if line_count == 0:
    #             headers = row
    #         elif row[0] == 'country/region' and row[1] == 'Netherlands':
    #             for idx,datum in enumerate(headers[6:]):
    #                 vervoertype = translate[row[2]]
    #                 percentagestr = row[idx+6]
    #                 if percentagestr:
    #                     initrecord(datum, metenisweten)
    #                     metenisweten[datum]['mobiliteit'][vervoertype] = float(percentagestr)
    #         line_count = line_count + 1

    print("Vaccinaties")
    filename = '../cache/rijksoverheid-coronadashboard-NL.json'
    # 2023-11-11 Corona Dashboard is changed...
    # with open(filename, 'r') as json_file:
    #     data = json.load(json_file)

    #     cachedDate = None
    #     cachedDateValid = False
    #     for record in data['vaccine_administered']['values']:
    #         if cachedDate != record['date_end_unix']:
    #             d = datetime.datetime.utcfromtimestamp(
    #                 int(record['date_end_unix']))
    #             if (datetime.datetime.date(d) > datetime.datetime.today().date()):
    #                 print(datetime.datetime.date(d).strftime('%Y-%m-%d')+' > ' +
    #                       datetime.datetime.today().date().strftime('%Y-%m-%d'))
    #                 cachedDateValid = False
    #             else:
    #                 cachedDateValid = True
    #                 datum = d.strftime('%Y-%m-%d')

    #         if not cachedDateValid:
    #             continue

    #         initrecord(datum, metenisweten)
    #         metenisweten[datum]['vaccinaties']['astra_zeneca'] = intOrNone(
    #             record['astra_zeneca'])
    #         metenisweten[datum]['vaccinaties']['pfizer'] = intOrNone(
    #             record['pfizer'])
    #         metenisweten[datum]['vaccinaties']['moderna'] = intOrNone(
    #             record['moderna'])
    #         metenisweten[datum]['vaccinaties']['janssen'] = intOrNone(
    #             record['janssen'])
    #         metenisweten[datum]['vaccinaties']['totaal'] = intOrNone(
    #             record['total'])
    #         # metenisweten[datum]['vaccinaties']['cure_vac']     = intOrNone(record['cure_vac'])
    #         # metenisweten[datum]['vaccinaties']['sanofi']       = intOrNone(record['sanofi'])

    #         previousPredictionDate = d
    #         laatste_totaal = intOrNone(record['total'])

    #         if intOrZero(record['janssen']) > 0 and intOrZero(record['total']) > 0:
    #             percentage_dubbele_vaccins = 1 - \
    #                 (intOrZero(record['janssen'])/intOrZero(record['total']))

    #     # Load all predictions

    #     # Vaccinatie administratie wordt niet meer (of niet op dezelfde manier) meer gedaan
    #     # voorspelling_vaccinaties = { }
    #     # if 'vaccine_administered_estimate' in data:
    #     #     for record in data['vaccine_administered_estimate']['values']:
    #     #         d = datetime.datetime.utcfromtimestamp(int(record['date_end_unix']))
    #     #         voorspelling_vaccinaties[d] = intOrNone(record['total'])
    #     #         # print(intOrNone(record['total']))
    #     # else:
    #     #     logError("No data['vaccine_administered_estimate']")

    #     # # Interpolate prediction to TODAY
    #     nextPredictionValue = 0
    #     # for key, value in voorspelling_vaccinaties.items():
    #     #     # Get first next date
    #     #     if key >= datetime.datetime.now():
    #     #         nextPredictionDate = key
    #     #         nextPredictionValue = value
    #     #         break

    #     if (nextPredictionValue > 0):
    #         # print("Laatste waarde %s")
    #         # print("VACCINATIES: previous %s, next %s" % (str(previousPredictionDate), str(nextPredictionDate)))
    #         # print("VACCINATIES: previous %s, next %s" % (str(previousPredictionValue), str(nextPredictionValue)))
    #         linearFactor = (datetime.datetime.now() - previousPredictionDate).total_seconds(
    #         ) / (nextPredictionDate - previousPredictionDate).total_seconds()
    #         linearValue = round(laatste_totaal + linearFactor *
    #                             (nextPredictionValue - laatste_totaal))

    #         datum = datetime.datetime.today().date().strftime('%Y-%m-%d')
    #         initrecord(datum, metenisweten)
    #         metenisweten[datum]['vaccinaties']['totaal_geschat'] = linearValue
    #         metenisweten[datum]['vaccinaties']['totaal_mensen_geschat'] = linearValue - \
    #             (linearValue*percentage_dubbele_vaccins)/2
    #     else:
    #         metenisweten[datum]['vaccinaties']['totaal_geschat'] = laatste_totaal
    #         metenisweten[datum]['vaccinaties']['totaal_mensen_geschat'] = laatste_totaal - (
    #             laatste_totaal*percentage_dubbele_vaccins)/2

    #     # print("VACCINATIES: previous %s, next %s" % (str(datum), str(linearValue)))

    #     # Vaccinaties worden niet meer (of niet meer op dezelde manier) bijgehouden
    #     # Get actual vaccine deliveries
    #     # if 'vaccine_delivery' in data:
    #     #     for record in data['vaccine_delivery']['values']:
    #     #         d = datetime.datetime.utcfromtimestamp(int(record['date_end_unix']))
    #     #         if (datetime.datetime.date(d) > datetime.datetime.today().date()):
    #     #             print(datetime.datetime.date(d).strftime('%Y-%m-%d')+' > '+datetime.datetime.today().date().strftime('%Y-%m-%d'))
    #     #             # Skip estimates from RIVM
    #     #             continue

    #     #         datum =  d.strftime('%Y-%m-%d')
    #     #         initrecord(datum, metenisweten)
    #     #         metenisweten[datum]['vaccinaties']['geleverd']       = intOrNone(record['total'])
    #     # else:
    #     #     logError("No data['vaccine_delivery']")

    #     # Hardcode start of vaccination at 0 in 2020
    #     datum = '2020-12-01'
    #     initrecord(datum, metenisweten)
    #     metenisweten[datum]['vaccinaties']['astra_zeneca'] = 0
    #     metenisweten[datum]['vaccinaties']['pfizer'] = 0
    #     metenisweten[datum]['vaccinaties']['cure_vac'] = 0
    #     metenisweten[datum]['vaccinaties']['janssen'] = 0
    #     metenisweten[datum]['vaccinaties']['moderna'] = 0
    #     metenisweten[datum]['vaccinaties']['sanofi'] = 0
    #     metenisweten[datum]['vaccinaties']['totaal'] = 0

    print("Calculate average number of ill people based on Rna measurements")
    dates = []
    rna = []
    rivmschattingratio = []

    # Record the newest date with more than 30 RNA measurements, which
    # is the last date we will use for estimates.
    for date in metenisweten:
        # Record last valid RNA date
        # print('RNA metingen '+date+' '+str(metenisweten[date]['RNA']['totaal_RNA_metingen']))
        if metenisweten[date]['RNA']['totaal_RNA_metingen'] > 30:
            dates.append(date)
            rna.append(metenisweten[date]['RNA']['RNA_per_100k_avg'])

    # Smooth
    rna_avg = double_savgol(rna, 2, 13, 1)

    # Compare to RIVM estimates and correct scale
    for idx, date in enumerate(dates):
        rivmschatting = metenisweten[date]['rivm_schatting_besmettelijk']['value']
        if rivmschatting and rivmschatting > 5000 and rna_avg[idx] > 1000:
            rivmschattingratio.append(rivmschatting/rna_avg[idx])
    averageratio = mean(rivmschattingratio)
    print("Average ratio between RIVM estimates and RNA data: " +
          str(round(averageratio, 5)))
    rna_avg = [x * averageratio for x in rna_avg]

    for i in range(len(dates)):
        date = dates[i]
        metenisweten[date]['RNA']['besmettelijk'] = max(
            1, rna_avg[i])  # Don't allow negative or 0 numbers

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

    print("Calculate average number of ill people based on tests and rna data (magic formula)")
    dates = []
    ziek = []
    for datum in metenisweten:
        if datum in metenisweten \
                and ('rivm_totaal_tests' in metenisweten[datum]) and metenisweten[datum]['rivm_totaal_tests'] != None \
                and ('rivm_totaal_tests_positief' in metenisweten[datum]) and metenisweten[datum]['rivm_totaal_tests_positief'] != None \
                and (metenisweten[datum]['RNA']['totaal_RNA_per_100k'] > 1):

            dates.append(datum)
            ziek.append(
                ((1000000*metenisweten[datum]['rivm_totaal_tests_positief']/metenisweten[datum]['rivm_totaal_tests'])
                 + (3 * metenisweten[datum]['rivm_totaal_tests'])
                    + (22 * metenisweten[datum]['rivm_totaal_tests_positief']))
                * log(metenisweten[datum]['RNA']['totaal_RNA_per_100k'], 10)
                / 44
            )

    ziek = smooth(ziek)
    for i in range(len(dates)):
        date = dates[i]
        metenisweten[date]['rolf_besmettelijk'] = ziek[i]

    print("Calculate totals")
    totaal_positief = 0
    totaal_opgenomen = 0
    totaal_overleden = 0
    for datum in metenisweten:
        totaal_positief += metenisweten[datum]['positief']
        totaal_opgenomen += metenisweten[datum]['nu_opgenomen']
        totaal_overleden += metenisweten[datum]['overleden']

        metenisweten[datum]['totaal_positief'] = totaal_positief
        metenisweten[datum]['totaal_opgenomen'] = totaal_opgenomen
        metenisweten[datum]['totaal_overleden'] = totaal_overleden

    # Write sorted data
    writeMetenIsWeten()
    writejson('../cache/testlocaties.json', testpunten)


def freshdata():
    if download() or not os.path.isfile('../data/daily-stats.json') or isnewer(__file__, '../data/daily-stats.json'):
        builddaily()

        # New way of doing things:
        process_Rt()
        process_Zkh()
        
        # Write processed and sorted data
        writeMetenIsWeten()
        return True
    elif os.stat('../data/daily-stats.json').st_mtime > (time.time() - 1200):
        # downloaded data is "fresh" for 20 minutes
        # This is a workaround so that all graphs get
        # created if scripts are called within 20 minutes after
        # building a new dataset.
        return True
    else:
        return False


def getDateRange(metenisweten):
    for datum in metenisweten:
        try:
            mindatum
        except NameError:
            mindatum = dateCache.parse(datum)

        try:
            maxdatum
        except NameError:
            maxdatum = dateCache.parse(datum)

        mindatum = min(mindatum, dateCache.parse(datum))
        maxdatum = max(maxdatum, dateCache.parse(datum))

    # Woraround to make graphs look the same when rendering "full width"
    mindatum = max(mindatum, dateCache.parse("2020-03-01"))
    date_range = [mindatum + datetime.timedelta(days=x)
                  for x in range(0, (maxdatum-mindatum).days+7)]
    
    print(maxdatum)
    return date_range


def printDict(d):
    print(json.dumps(d, indent=4))


if __name__ == "__main__":
    freshdata()
