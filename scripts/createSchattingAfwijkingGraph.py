#!/usr/bin/env python3
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
from dateutil import parser
import datetime
import modules.brondata as brondata
from math import log
from modules.brondata import decimalstring
from modules.datautil import runIfNewData

runIfNewData(__file__)

metenisweten = brondata.readjson('../cache/daily-stats.json')

alpha = {
    'x' : [],
    'y' : []
}

beta = {
    'x' : [],
    'y' : [],
    'min' : [],
    'max' : []
}

tetascale=50000
teta = {
    'x' : [],
    'y' : []
}

gamma = {
    'x' : [],
    'y' : [],
}

debug=False

for datum in metenisweten:
    # if metenisweten[datum]['RNA_per_ml_avg']:
    #     alpha['x'].append(parser.parse(datum))
    #     alpha['y'].append(metenisweten[datum]['RNA_per_ml_avg'])

    if metenisweten[datum]['rivm_schatting_besmettelijk']['value']:
        alpha['x'].append(parser.parse(datum))
        alpha['y'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['value'])

    # if metenisweten[datum]['RNA']['besmettelijk']:
    #     beta['x'].append(parser.parse(datum))
    #     beta['y'].append(metenisweten[datum]['RNA']['besmettelijk'])
    #     beta['min'].append(metenisweten[datum]['RNA']['besmettelijk'] * (1-metenisweten[datum]['RNA']['besmettelijk_error']))
    #     beta['max'].append(metenisweten[datum]['RNA']['besmettelijk'] * (1+metenisweten[datum]['RNA']['besmettelijk_error']))

    if metenisweten[datum]['rolf_besmettelijk']:
        beta['x'].append(parser.parse(datum))
        if debug:
            beta['y'].append(
                    ( \
                        (1000000*metenisweten[datum]['rivm_totaal_tests_positief']/metenisweten[datum]['rivm_totaal_tests']) \
                        + (3 * metenisweten[datum]['rivm_totaal_tests']) \
                        + (22 * metenisweten[datum]['rivm_totaal_tests_positief']) \
                    ) * (log(metenisweten[datum]['RNA']['totaal_RNA_per_ml'],10)) \
                    /14)
        else:
            beta['y'].append(metenisweten[datum]['rolf_besmettelijk'])

        beta['min'].append(metenisweten[datum]['rolf_besmettelijk'] * 0.7)
        beta['max'].append(metenisweten[datum]['rolf_besmettelijk'] * 1.3)

    # if metenisweten[datum]['rivm_schatting_besmettelijk']['value'] and metenisweten[datum]['RNA']['besmettelijk']:
    #     gamma['x'].append(parser.parse(datum))
    #     gamma['y'].append(100 - 100 * metenisweten[datum]['rivm_schatting_besmettelijk']['value'] / metenisweten[datum]['RNA']['besmettelijk'])

    if metenisweten[datum]['rivm_schatting_besmettelijk']['value'] and metenisweten[datum]['rolf_besmettelijk']:
        gamma['x'].append(parser.parse(datum))
        gamma['y'].append(100 - 100 * metenisweten[datum]['rivm_schatting_besmettelijk']['value'] / metenisweten[datum]['rolf_besmettelijk'])

    if metenisweten[datum]['rivm_infectieradar_perc']:
        teta['x'].append(parser.parse(datum))
        teta['y'].append(metenisweten[datum]['rivm_infectieradar_perc'] * tetascale)

        
if debug:
    beta['y'] = brondata.smooth(beta['y'])

teta['y'] = brondata.smooth(teta['y'])

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
ax1.plot(alpha['x'], alpha['y'], color='red', label='Schatting zieken RIVM')
# ax1.plot(beta['x'], beta['y'], color='steelblue', label='beta')

# ax2.plot(alpha['x'], alpha['y'], c olor='steelblue', label='alpha')
# ax1.plot(beta['x'], beta['y'], color='blue', label='Schatting zieken @rolfje obv RNA in RWZI')
ax1.plot(beta['x'], beta['y'], color='blue', label='Schatting zieken @rolfje obv tests en RNA in RWZI')

ax1.fill_between(
    beta['x'],
    beta['min'], 
    beta['max'],
    facecolor='blue', alpha=0.1, interpolate=True)

ax1.plot(teta['x'], teta['y'], color='cyan', label='Infectieradar COVID-19 klachten (percentage x'+decimalstring(tetascale)+')')

ax2.plot(gamma['x'], gamma['y'], color='lightgreen', label='Afwijking @rolfje t.o.v. RIVM schatting in %')

ax1.set_ylim([0, 400000])
ax2.set_ylim([-200, 200])

ax1.set_xlabel("Datum")

gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
plt.title('Afwijking schatting @rolfje t.o.v. RIVM schatting, '+gegenereerd_op)

ax1.legend(loc="upper left")
ax2.legend(loc="upper right")
plt.savefig("../docs/graphs/schattingafwijking.svg", format="svg")
#plt.show()

