#!/usr/bin/env python3
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
from dateutil import parser
from statistics import mean
import datetime
import json
import modules.brondata as brondata

brondata.freshdata()
metenisweten = brondata.readjson('../cache/daily-stats.json')

alpha = {
    'x' : [],
    'y' : []
}

beta = {
    'x' : [],
    'y' : []
}

gamma = {
    'x' : [],
    'min' : [],
    'max' : []
}

for datum in metenisweten:
    # if metenisweten[datum]['RNA_per_ml_avg']:
    #     alpha['x'].append(parser.parse(datum))
    #     alpha['y'].append(metenisweten[datum]['RNA_per_ml_avg'])

    if metenisweten[datum]['rivm_schatting_besmettelijk']['value']:
        alpha['x'].append(parser.parse(datum))
        alpha['y'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['value'])

    if metenisweten[datum]['RNA']['besmettelijk']:
        beta['x'].append(parser.parse(datum))
        beta['y'].append(metenisweten[datum]['RNA']['besmettelijk'])

        gamma['x'].append(parser.parse(datum))
        gamma['min'].append(metenisweten[datum]['RNA']['besmettelijk'] * (1-metenisweten[datum]['RNA']['besmettelijk_error']))
        gamma['max'].append(metenisweten[datum]['RNA']['besmettelijk'] * (1+metenisweten[datum]['RNA']['besmettelijk_error']))

print('Generating test graph...')

fig, ax1 = plt.subplots(figsize=(10, 5))
fig.subplots_adjust(top=0.92, bottom=0.13, left=0.09, right=0.91)

# ax2 = plt.twinx()

#plt.figure(figsize =(10,5))
ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)
# ax2.grid(which='both', axis='both', linestyle='-.',
#          color='gray', linewidth=1, alpha=0.3)

# Plot cases per dag
ax1.plot(alpha['x'], alpha['y'], color='red', label='alpha/schatting zieken RIVM')
# ax1.plot(beta['x'], beta['y'], color='steelblue', label='beta')

# ax2.plot(alpha['x'], alpha['y'], c olor='steelblue', label='alpha')
ax1.plot(beta['x'], beta['y'], color='green', label='beta/schatting zieken @rolfje obv RNA in RWZI per # inwoners per veiligheidsregio')

ax1.fill_between(
    gamma['x'],
    gamma['min'], 
    gamma['max'],
    facecolor='steelblue', alpha=0.1, interpolate=True)

ax1.set_xlabel("Datum")
plt.title('Testplot')

ax1.legend(loc="upper left")
# ax2.legend(loc="upper right")
plt.savefig("../docs/graphs/testplot.svg", format="svg")
#plt.show()

