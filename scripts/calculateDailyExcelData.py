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
testpunten = brondata.readjson('../cache/testlocaties.json')
metenisweten = brondata.readjson('../cache/daily-stats.json')

# ----------------------- Generate CSV output -----------------------------

filename='../data/'+datetime.now().strftime('%Y-%m-%d')+"-RIVM-NICE.csv"
print('Writing '+filename)
with open(filename,'w') as file: 
    file.write('"Datum"\t"Positief getest werkelijk"\t"Opgenomen (geweest) in ziekenhuis"\t"Overleden"\t"Opgenomen (geweest) op IC"\t"Op dit moment op IC"\n')
    totaal_positief = 0
    totaal_opgenomen = 0
    totaal_overleden = 0

    for datum in metenisweten:
        file.write(
            datum + '\t' +
            str(metenisweten[datum]['totaal_positief']) + '\t' +
            str(metenisweten[datum]['totaal_opgenomen']) + '\t' +    
            str(metenisweten[datum]['totaal_overleden']) + '\t' +
            str(metenisweten[datum]['geweest_op_ic']) + '\t' +
            str(metenisweten[datum]['nu_op_ic']) + '\n'
        )
        totaal_positief = max(totaal_positief, metenisweten[datum]['totaal_positief'])
        totaal_opgenomen = max(totaal_opgenomen, metenisweten[datum]['totaal_opgenomen'])
        totaal_overleden = max(totaal_overleden, metenisweten[datum]['totaal_overleden'])

with open('../data/runs.csv','a') as file:
    file.write(
        datetime.now().strftime('%Y-%m-%d') + '\t' +
        str(totaal_positief) + '\t' +
        str(totaal_opgenomen) + '\t' +
        str(totaal_overleden) + '\n'
    )

# --------------------- Generate markdown versions

filename='../data/'+datetime.now().strftime('%Y-%m-%d')+"-RIVM-NICE.md"
print('Writing '+filename)
with open(filename,'w') as file: 
    file.write('| Datum | Positief getest werkelijk | Opgenomen (geweest) in ziekenhuis | Overleden | Opgenomen (geweest) op IC | Op dit moment op IC |\n')
    file.write('|-------|--------------------------:|----------------------------------:|----------:|--------------------------:|--------------------:|\n')
    for datum in metenisweten:
        file.write('| ' + 
            datum + ' | ' +
            str(metenisweten[datum]['totaal_positief']) + ' | ' +
            str(metenisweten[datum]['totaal_opgenomen']) + ' | ' +    
            str(metenisweten[datum]['totaal_overleden']) + ' | ' +
            str(metenisweten[datum]['geweest_op_ic']) + ' | ' +
            str(metenisweten[datum]['nu_op_ic']) + ' |\n'
        )

filename='../data/'+datetime.now().strftime('%Y-%m-%d')+"-testlocaties.md"
print('Writing '+filename)
with open(filename,'w') as file: 
    file.write('| Locatie | Positieve tests |\n')
    file.write('|---------|----------------:|\n')
    for testpunt in testpunten:
        file.write('| ' + testpunt.ljust(40) + ' | ' + str(testpunten[testpunt]).rjust(5) + ' |\n') 

print('Done.')
