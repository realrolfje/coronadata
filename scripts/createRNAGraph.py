#!/usr/bin/env python3
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
from dateutil import parser
from statistics import mean
import datetime
import json
import modules.brondata as brondata
from modules.brondata import decimalstring, smooth
from scipy.ndimage.filters import uniform_filter1d

brondata.freshdata()
metenisweten = brondata.readjson('../cache/daily-stats.json')

print('Generating RNA graph...')

RNA_per_ml_avg = {
    'x':[],
    'y':[],
    'smooth' : []
}

RNA_populatie_dekking = {
    'x':[],
    'y':[],
}

for datum in metenisweten:
    if metenisweten[datum]['RNA']['totaal_RNA_metingen'] > 0:
        RNA_per_ml_avg['x'].append(parser.parse(datum))
        RNA_per_ml_avg['y'].append(metenisweten[datum]['RNA']['RNA_per_ml_avg'])
    if metenisweten[datum]['RNA']['populatie_dekking']:
        RNA_populatie_dekking['x'].append(parser.parse(datum))
        RNA_populatie_dekking['y'].append(metenisweten[datum]['RNA']['populatie_dekking'] * 100)


plt.figure(figsize=(10,3))

fig, ax1 = plt.subplots(figsize=(10, 3))
fig.subplots_adjust(bottom=0.2, left=0.09, right=0.91)
ax2 = plt.twinx()

ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)
ax1.plot(RNA_per_ml_avg['x'], smooth(RNA_per_ml_avg['y']), color='green', label='RNA per mL rioolwater (gemiddeld)')

# RNA_per_ml_avg['besmettelijk'] = uniform_filter1d(RNA_per_ml_avg['y'], size=20)
# plt.plot(RNA_per_ml_avg['x'], RNA_per_ml_avg['besmettelijk'], color='green', label='Geschat besmettelijk')

ax1.fill_between(RNA_per_ml_avg['x'], 0, RNA_per_ml_avg['y'],facecolor='green', alpha=0.3, interpolate=True)

# laat huidige datum zien met vertikale lijn
ax1.axvline(datetime.date.today(), color='teal', linewidth=0.15)

ax2.plot(RNA_populatie_dekking['x'], smooth(RNA_populatie_dekking['y']), color='orange', label='geschatte populatie dekking %')


axes = plt.gca()
axes.set_xlim([parser.parse("2020-02-01"),datetime.date.today() + datetime.timedelta(days=7)])

ax1.set_ylim([0,4000])
ax1.set_ylabel("RNA per mL")
ax1.set_xlabel("Datum")

ax2.set_ylim([0,100])
ax2.set_ylabel("% populatie")
ax2.set_yticks([0,25,50,75,100])

ax1.legend(loc="upper left")
ax2.legend(loc="upper right")

plt.figtext(0.40,0.6, 
         "\"Je plee liegt niet\" - Rolf",
         color="gray",
         bbox=dict(facecolor='white', alpha=1.0, 
         edgecolor='white'),
         zorder=10)

gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
plt.title('Concentratie SARS-CoV-2 RNA per mL rioolwater, '+gegenereerd_op)

footerleft="Gegenereerd op "+gegenereerd_op+".\nSource code: http://github.com/realrolfje/coronadata"
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")

footerright="Bron: https://data.rivm.nl/covid-19"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

plt.savefig("../docs/graphs/rna-in-rioolwater.svg", format="svg")


