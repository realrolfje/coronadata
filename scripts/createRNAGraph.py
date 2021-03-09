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
date_range = brondata.getDateRange(metenisweten)

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
# ax2 = plt.twinx()

ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)
ax1.plot(RNA_per_ml_avg['x'], smooth(RNA_per_ml_avg['y']), color='green', label='RNA per milliliter rioolwater (gemiddeld)')

# RNA_per_ml_avg['besmettelijk'] = uniform_filter1d(RNA_per_ml_avg['y'], size=20)
# plt.plot(RNA_per_ml_avg['x'], RNA_per_ml_avg['besmettelijk'], color='green', label='Geschat besmettelijk')

ax1.fill_between(RNA_per_ml_avg['x'], 0, RNA_per_ml_avg['y'],facecolor='green', alpha=0.3, interpolate=True)

# laat huidige datum zien met vertikale lijn
plt.figtext(0.885,0.19, 
         datetime.datetime.now().strftime("%d"), 
         color="red",
         fontsize=8,
         bbox=dict(facecolor='white', alpha=0.9, pad=0,
         edgecolor='white'),
         zorder=10)
ax1.axvline(datetime.date.today(), color='red', linewidth=0.5)

#  ax2.plot(RNA_populatie_dekking['x'], smooth(RNA_populatie_dekking['y']), color='orange', label='geschatte populatie dekking %')


axes = plt.gca()
axes.set_xlim([parser.parse("2020-03-01"),date_range[-1]])

ax1.set_ylim([0,4000])
ax1.set_ylabel("RNA per milliliter")
ax1.set_xlabel("Datum")

# ax2.set_ylim([0,100])
# ax2.set_ylabel("% populatie")
# ax2.set_yticks([0,25,50,75,100])

ax1.legend(loc="upper left")
# ax2.legend(loc="upper right")

plt.figtext(0.30,0.6, 
         "\"Je plee liegt niet\" - Rolf",
         color="gray",
         bbox=dict(facecolor='white', alpha=1.0, 
         edgecolor='white'),
         zorder=10)

data_tot=RNA_per_ml_avg['x'][-1].strftime("%Y-%m-%d")
gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
plt.title('Concentratie SARS-CoV-2 RNA per ml rioolwater')

footerleft="Gegenereerd op "+gegenereerd_op+" o.b.v. data tot "+data_tot+".\nSource code: http://github.com/realrolfje/coronadata"
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")

footerright="Bron: https://data.rivm.nl/covid-19"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

plt.savefig("../docs/graphs/rna-in-rioolwater.svg", format="svg")


