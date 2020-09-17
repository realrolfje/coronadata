#!/usr/bin/env python3
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
from dateutil import parser
from statistics import mean
import datetime
import json
import modules.brondata as brondata
from scipy.ndimage.filters import uniform_filter1d

brondata.freshdata()
metenisweten = brondata.readjson('../cache/daily-stats.json')

print('Generating RNA graph...')

RNA_per_ml_avg = {
    'x':[],
    'y':[],
    'besmettelijk':[]
}

for datum in metenisweten:
    if metenisweten[datum]['totaal_RNA_metingen'] > 0:
        RNA_per_ml_avg['x'].append(parser.parse(datum))
        RNA_per_ml_avg['y'].append(metenisweten[datum]['RNA_per_ml_avg'])



def decimalstring(number):
    return "{:,}".format(number).replace(',','.')

plt.figure(figsize=(10,3))
plt.subplots_adjust(bottom=0.2, left=0.09, right=0.91)
plt.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)
plt.plot(RNA_per_ml_avg['x'], RNA_per_ml_avg['y'], color='green', label='RNA per mL rioolwater (gemiddeld)')

# RNA_per_ml_avg['besmettelijk'] = uniform_filter1d(RNA_per_ml_avg['y'], size=20)
# plt.plot(RNA_per_ml_avg['x'], RNA_per_ml_avg['besmettelijk'], color='green', label='Geschat besmettelijk')

plt.fill_between(RNA_per_ml_avg['x'], 0, RNA_per_ml_avg['y'],facecolor='green', alpha=0.3, interpolate=True)

# laat huidige datum zien met vertikale lijn
plt.axvline(datetime.date.today(), color='teal', linewidth=0.15)

axes = plt.gca()
axes.set_ylim([0,2000])
axes.set_xlim([parser.parse("2020-02-01"),datetime.date.today() + datetime.timedelta(days=7)])
axes.set_xlabel("Datum")
axes.set_ylabel("RNA per mL")

gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
plt.title('Concentratie SARS-CoV-2 RNA per mL rioolwater, '+gegenereerd_op)

footerleft="Gegenereerd op "+gegenereerd_op+".\nSource code: http://github.com/realrolfje/coronadata"
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")

footerright="Bron: https://data.rivm.nl/covid-19"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

plt.savefig("../graphs/rna-in-rioolwater.png", format="png")
plt.savefig("../graphs/rna-in-rioolwater.svg", format="svg")


