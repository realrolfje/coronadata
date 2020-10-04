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
    'y' : []
}

for datum in metenisweten:
    # if metenisweten[datum]['RNA_per_ml_avg']:
    #     alpha['x'].append(parser.parse(datum))
    #     alpha['y'].append(metenisweten[datum]['RNA_per_ml_avg'])

    if metenisweten[datum]['nu_op_ic']:
        alpha['x'].append(parser.parse(datum))
        alpha['y'].append(metenisweten[datum]['nu_op_ic'])

    if metenisweten[datum]['rivm_schatting_besmettelijk']['value']:
        beta['x'].append(parser.parse(datum))
        beta['y'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['value'])

    if metenisweten[datum]['opgenomen']:
        gamma['x'].append(parser.parse(datum))
        gamma['y'].append(metenisweten[datum]['opgenomen'])

print('Generating test graph...')

fig, ax1 = plt.subplots(figsize=(10, 5))
fig.subplots_adjust(top=0.92, bottom=0.13, left=0.09, right=0.91)

ax2 = plt.twinx()

#plt.figure(figsize =(10,5))
ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)
ax2.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)

# Plot cases per dag
ax1.plot(alpha['x'], alpha['y'], color='red', label='alpha')
# ax1.plot(beta['x'], beta['y'], color='steelblue', label='beta')

# ax2.plot(alpha['x'], alpha['y'], c olor='steelblue', label='alpha')
ax2.plot(beta['x'], beta['y'], color='green', label='beta')

ax1.plot(gamma['x'], gamma['y'], color='orange', label='gamma')


ax1.set_xlabel("Datum")
plt.title('Testplot')

ax1.legend(loc="upper left")
ax2.legend(loc="upper right")
plt.savefig("../docs/graphs/testplot.svg", format="svg")
#plt.show()

