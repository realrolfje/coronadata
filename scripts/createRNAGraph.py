#!/usr/bin/env python3
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
from dateutil import parser
from statistics import mean
import datetime
import modules.arguments as arguments
import modules.brondata as brondata
from modules.brondata import decimalstring, smooth
from scipy.ndimage.filters import uniform_filter1d

print("------------ %s ------------" % __file__)
if (brondata.freshdata() or brondata.isnewer(__file__, '../cache/daily-stats.json') or arguments.isForce()):
    print("New data, regenerate output.")
else:
    print("No fresh data, and unchanged code. Exit.")
    exit(0)

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

date_range = brondata.getDateRange(metenisweten)
lastDays = arguments.lastDays()
if (lastDays>0):
    date_range = date_range[-lastDays:]

for d in date_range:
    datum = d.strftime("%Y-%m-%d")

    if datum in metenisweten and metenisweten[datum]['RNA']['totaal_RNA_metingen'] > 0\
        and  metenisweten[datum]['RNA']['RNA_per_ml_avg'] < 8000:
        # The < 8000 is to remove strange 9700 spike in measurements in may

        RNA_per_ml_avg['x'].append(parser.parse(datum))
        RNA_per_ml_avg['y'].append(metenisweten[datum]['RNA']['RNA_per_ml_avg'])
    if datum in metenisweten and metenisweten[datum]['RNA']['populatie_dekking']:
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

# Put vertical line at current day
plt.text(
    x=datetime.date.today(),
    y=0,
    s=datetime.datetime.now().strftime("%d"), 
    color="white",
    fontsize=8,
    ha="center",
    va="center",
    bbox=dict(boxstyle='round,pad=0.1', facecolor='red', alpha=1, edgecolor='red'),
    zorder=10
)
plt.axvline(datetime.date.today(), color='red', linewidth=0.5)

#  ax2.plot(RNA_populatie_dekking['x'], smooth(RNA_populatie_dekking['y']), color='orange', label='geschatte populatie dekking %')


axes = plt.gca()
axes.set_xlim([date_range[0],date_range[-1]])

ax1.set_ylim([0,6000])
ax1.set_ylabel("RNA per milliliter")
ax1.set_xlabel("Datum")

# ax2.set_ylim([0,100])
# ax2.set_ylabel("% populatie")
# ax2.set_yticks([0,25,50,75,100])

ax1.legend(loc="upper left")
# ax2.legend(loc="upper right")

plt.figtext(0.60,0.7, 
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

if (lastDays > 0):
    plt.savefig("../docs/graphs/rna-in-rioolwater"+"-"+str(lastDays)+".svg", format="svg")
else:
    plt.savefig("../docs/graphs/rna-in-rioolwater.svg", format="svg")
