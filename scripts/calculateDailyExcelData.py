#!/usr/bin/env python3 
#
# Haalt COVID-19 testresultaten op bij RIVM, en IC opnames bij NICE,
# correlleert ze en schrijft ze naar een file die geimporteerd kan
# worden in excel.
#

import urllib.request
import json 
import sys
from datetime import datetime
import modules.brondata as brondata

brondata.download()

# -------------------- Get data from RIVM -----------------
print('Loading data from RIVM...')
with open('../cache/COVID-19_casus_landelijk.json', 'r') as json_file:
    data = json.load(json_file)
    metenisweten = { }
    for record in data:
        if (record['Date_statistics'] not in metenisweten):
            metenisweten[record['Date_statistics']] = {
                'positief': 0,
                'opgenomen': 0,
                'overleden': 0,
                'geweest_op_ic': 0,
                'nu_op_ic': 0
            }
        metenisweten[record['Date_statistics']]['positief'] += 1
        if (record['Hospital_admission'] == 'Yes'):
                metenisweten[record['Date_statistics']]['opgenomen'] += 1
        if (record['Deceased'] == 'Yes'):
                metenisweten[record['Date_statistics']]['overleden'] += 1

# -------------------- Get geweest op IC van NICE -----------------------
print('Loading data 1/2 from NICE...')
with open('../cache/NICE-intake-cumulative.json', 'r') as json_file:
    data = json.load(json_file)
    for measurement in data:
        if (measurement['date'] not in metenisweten):
            metenisweten[measurement['date']] = {
                'positief': 0,
                'opgenomen': 0,
                'overleden': 0,
                'geweest_op_ic': 0,
                'nu_op_ic': 0
            }
        metenisweten[measurement['date']]['geweest_op_ic'] += measurement['value']

# -------------------- Get nu op IC van NICE -----------------------
print('Loading data 2/2 from NICE...')
with open('../cache/NICE-intake-count.json', 'r') as json_file:
    data = json.load(json_file)
    for measurement in data:
        if (measurement['date'] not in metenisweten):
            metenisweten[measurement['date']] = {
                'positief': 0,
                'opgenomen': 0,
                'overleden': 0,
                'geweest_op_ic': 0,
                'nu_op_ic': 0
            }
        metenisweten[measurement['date']]['nu_op_ic'] += measurement['value']


# ---------------------- Calculate totals -----------------------------
print('Calculating totals...')
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

# ----------------------- Generate CSV output -----------------------------

csvfile='../data/'+datetime.now().strftime('%Y-%m-%d')+"-RIVM-NICE.csv"
print('Writing '+csvfile)
with open(csvfile,'w') as file: 
    file.write('"Datum"\t"Positief getest werkelijk"\t"Opgenomen (geweest) in ziekenhuis"\t"Overleden"\t"Opgenomen (geweest) op IC"\t"Op dit moment op IC"\n')
    for datum in metenisweten:
        file.write(
            datum + '\t' +
            str(metenisweten[datum]['totaal_positief']) + '\t' +
            str(metenisweten[datum]['totaal_opgenomen']) + '\t' +    
            str(metenisweten[datum]['totaal_overleden']) + '\t' +
            str(metenisweten[datum]['geweest_op_ic']) + '\t' +
            str(metenisweten[datum]['nu_op_ic']) + '\n'
        )


with open('../data/runs.csv','a') as file:
    file.write(
        datetime.now().strftime('%Y-%m-%d') + '\t' +
        str(totaal_positief) + '\t' +
        str(totaal_opgenomen) + '\t' +
        str(totaal_overleden) + '\n'
    )

print('Printing to stdout for easier copy-pasting.')
with open(csvfile,'r') as file: 
    for line in file:
        sys.stdout.write(line)

print('Done.')
