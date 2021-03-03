#!/usr/bin/env python3
#
from matplotlib import pyplot as plt
from dateutil import parser
import modules.brondata as brondata
from modules.brondata import decimalstring, smooth
from datetime import datetime, date
from math import log

#brondata.freshdata()
metenisweten = brondata.readjson('../cache/daily-stats.json')
events = brondata.readjson('../data/measures-events.json')

testgrafiek = {
    'x': [],
    'rivm_schatting': [],
    'rivm_totaal_tests' :          [],
    'rivm_totaal_tests_positief' :[],
    'rivm_tests_perc'        :    [],
    'rna'        :    [],
    
}

date_range = brondata.getDateRange(metenisweten)

for d in date_range:
    datum = d.strftime("%Y-%m-%d")
    if datum in metenisweten \
        and metenisweten[datum]['rivm_schatting_besmettelijk']['value'] != None \
        and ('rivm_totaal_tests' in metenisweten[datum]) and metenisweten[datum]['rivm_totaal_tests'] != None \
        and ('rivm_totaal_tests_positief' in metenisweten[datum]) and metenisweten[datum]['rivm_totaal_tests_positief'] != None \
        and (metenisweten[datum]['RNA']['totaal_RNA_per_ml'] > 1) :


        testgrafiek['x'].append(d)
        testgrafiek['rivm_schatting'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['value'])
        testgrafiek['rivm_totaal_tests'].append(metenisweten[datum]['rivm_totaal_tests'])
        testgrafiek['rivm_totaal_tests_positief'].append(metenisweten[datum]['rivm_totaal_tests_positief'])
        testgrafiek['rivm_tests_perc'].append(100*testgrafiek['rivm_totaal_tests_positief'][-1]/testgrafiek['rivm_totaal_tests'][-1])
        if len(testgrafiek['rna']) < 2:
            testgrafiek['rna'].append(metenisweten[datum]['RNA']['totaal_RNA_per_ml'])
        else:
            testgrafiek['rna'].append((metenisweten[datum]['RNA']['totaal_RNA_per_ml'] + testgrafiek['rna'][-1] + testgrafiek['rna'][-2])/3)


if len(testgrafiek['x']) < 1:
    print('no data')
    exit(1)


print('Generating vaccination graph...')
fig, ax1 = plt.subplots(figsize=(10, 5))
fig.subplots_adjust(top=0.92, bottom=0.13, left=0.09, right=0.91)

ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)

ax1.set_xlabel("Datum")
# ax1.set_ylabel("Aantal prikken")

ax1.plot(testgrafiek['x'], testgrafiek['rivm_schatting'], color='red', label='RIVM schatting')

ax1.plot(testgrafiek['x'], testgrafiek['rivm_totaal_tests'], color='blue', label='tests')
ax1.plot(testgrafiek['x'], testgrafiek['rivm_totaal_tests_positief'], color='pink', label='positief')
ax1.plot(testgrafiek['x'], testgrafiek['rivm_tests_perc'], color='yellow', label='percentage')
ax1.plot(testgrafiek['x'], testgrafiek['rna'], color='lightgreen', label='rna')

ax1.plot(testgrafiek['x'], 
        # [(3*t) for p, t in zip(testgrafiek['rivm_tests_perc'], testgrafiek['rivm_totaal_tests'])], 
        # [(10000*p) for p, t in zip(testgrafiek['rivm_tests_perc'], testgrafiek['rivm_totaal_tests'])], 
        smooth([((10000*perc)+(3*tot)+(22*pos))*(log(rna,10)/3.8)/3 for perc, tot, pos, rna in zip(testgrafiek['rivm_tests_perc'], testgrafiek['rivm_totaal_tests'], testgrafiek['rivm_totaal_tests_positief'], testgrafiek['rivm_totaal_tests_positief'])]), 
        color='green',
        label='Rolf schatting')

# laat huidige datum zien met vertikale lijn
plt.figtext(0.885,0.125, 
         datetime.now().strftime("%d"), 
         color="red",
         fontsize=8,
         bbox=dict(facecolor='white', alpha=0.9, pad=0,
         edgecolor='white'),
         zorder=10)
ax1.axvline(date.today(), color='red', linewidth=0.5)

# ax1.set_yticks      ([0.1,    0.2,   0.3,   0.4,   0.5,   0.6,   0.7,   0.8,  0.9,   1])
# ax1.set_yticklabels([ '10%',  '20%', '30%', '40%', '50%', '60%', '70%','80%','90%','100%'])

plt.gca().set_xlim([parser.parse("2020-03-01"), date_range[-1]])

gegenereerd_op=datetime.now().strftime("%Y-%m-%d %H:%M")
data_tot=testgrafiek['x'][-1].strftime("%Y-%m-%d")
filedate=data_tot

plt.title('Zoek een patroon')

footerleft="Gegenereerd op "+gegenereerd_op+", o.b.v. data tot "+data_tot+".\nSource code: http://github.com/realrolfje/coronadata"
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")


footerright="Publicatiedatum RIVM "+filedate+".\nBron: https://www.rivm.nl/covid-19-vaccinatie/"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")


ax1.legend(loc="upper left")

plt.show()

# plt.savefig("../docs/graphs/vaccinaties.svg", format="svg")
