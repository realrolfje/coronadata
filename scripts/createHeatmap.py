#!/usr/bin/env python3
#
# pip3 install matplotlib

import numpy as np
from matplotlib import pyplot as plt
from dateutil import parser
from statistics import mean
from dateutil.relativedelta import relativedelta
import datetime
import json
import modules.brondata as brondata
from modules.brondata import decimalstring, isnewer

print("------------ %s ------------" % __file__)
if not (brondata.freshdata() or brondata.isnewer(__file__, '../cache/daily-stats.json')):
    print("No fresh data, and unchanged code. Exit.")
    exit(0)
else:
    print("New data, regenerate output.")

print("Generating date/age heatmap.")

xlabels = []
x = []
y = []

startdate = parser.parse('2020-03-01')

weightsmap={}

# THe heatmap data is already in metenisweten, we can optimze. Complete this:
# metenisweten = brondata.readjson('../cache/daily-stats.json')
# print("Converting records to x/y data")
# for date_statistics in metenisweten:
#     if date_statistics > startdate:
#         for age in metenisweten[date_statistics]['besmettingleeftijd']:
#             datax = (date_statistics - startdate).days
#             datay = metenisweten[date_statistics]['besmettingleeftijd']


with open('../cache/COVID-19_casus_landelijk.json', 'r') as json_file:
    data = json.load(json_file)
    print("Converting records to x/y data")
    for record in data:
        date_statistics = parser.parse(record['Date_statistics'])
        if date_statistics > startdate:
            try:
                datax = (date_statistics - startdate).days
                datay = int(record['Agegroup'].split('-')[0].split('+')[0])+5
                filedate = record['Date_file']
                x.append(datax)
                y.append(datay)

                # if datax not in weightsmap:
                #     weightsmap[datax] = 1
                # else:
                #     weightsmap[datax] = weightsmap[datax] + 1

            except ValueError:
                # print('ERROR '+record['Date_statistics'] + ' | ' + record['Agegroup'])
                pass

# print("Calculating weights.")
# weights=[]
# for d in x:
#     weights.append(1./weightsmap[d])

# Averages
gemiddeldeleeftijd = {
    'x': [],
    'y': []
}

metenisweten = brondata.readjson('../cache/daily-stats.json')
date_range = brondata.getDateRange(metenisweten)
for d in date_range:
    datum = d.strftime("%Y-%m-%d")
    if datum in metenisweten and metenisweten[datum]['besmettingleeftijd_gemiddeld'] is not None:
        gemiddeldeleeftijd['x'].append(d)
        gemiddeldeleeftijd['y'].append(metenisweten[datum]['besmettingleeftijd_gemiddeld'])

gemiddeldlaatsteweek = int(round(sum(gemiddeldeleeftijd['y'][-7:])/7))

gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

fig, heatmap = plt.subplots(figsize=(10, 4))
fig.subplots_adjust(top=0.92, bottom=0.17, left=0.09, right=0.91)
averages = plt.twinx()

plt.title('Positieve tests per leeftijdsgroep')

print("Plotting heatmap, "+str(len(x))+"x"+str(len(y)))

# Gewogen:
#plt.hist2d(x, y, bins=[x[-1]+7,10], range=[[0,x[-1]+7],[0,100]], cmap='inferno', weights=weights)

# Ongewogen:
heatmap.hist2d(x, y, bins=[x[-1]+7,10], range=[[0,x[-1]+7],[0,100]], cmin=1, cmap='Blues') # inferno is also a good one


leeftijdx = [(x-startdate).days for x in gemiddeldeleeftijd['x']]
averages.plot(leeftijdx, gemiddeldeleeftijd['y'], color='darkred', alpha=0.5, label='Gemiddelde leeftijd (laatste week: '+str(gemiddeldlaatsteweek)+')')

averages.legend(loc="upper right")

heatmap.set_ylim([0, 100])
averages.set_ylim([0,100])

# Dirty stuff to get x labels (needs cleanup)
xlabeldates = [startdate + relativedelta(months=x) for x in range(gemiddeldeleeftijd['x'][-1].month - startdate.month + ((gemiddeldeleeftijd['x'][-1].year - startdate.year) * 12) + 1)]
xlabels = []
xlocs = []
for label in xlabeldates:
    xlabels.append(label.strftime("%Y-%m"))
    xlocs.append((label - startdate).days)
locs, labels = plt.xticks(xlocs, xlabels)

# Labels and tickmarks
heatmap.set_xlabel("Datum")
heatmap.set_ylabel("Leeftijd")

# laat huidige datum zien met vertikale lijn
plt.figtext(0.885,0.165, 
         datetime.datetime.now().strftime("%d"), 
         color="red",
         fontsize=8,
         bbox=dict(facecolor='white', alpha=0.9, pad=0,
         edgecolor='white'),
         zorder=10)

averages.axvline((datetime.date.today() - startdate.date()).days, color='red', linewidth=0.5)

data_tot = gemiddeldeleeftijd['x'][-1].strftime("%Y-%m-%d")
footerleft="Gegenereerd op "+gegenereerd_op+" o.b.v. data tot "+data_tot+".\nSource code: http://github.com/realrolfje/coronadata"
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")

footerright="Publicatiedatum RIVM "+filedate+".\nBron: https://data.rivm.nl/covid-19"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

heatmap.grid(which='both', axis='both', linestyle='-.',
            color='gray', linewidth=1, alpha=0.3)

plt.savefig("../docs/graphs/besmettingen-leeftijd.svg", format="svg")

# plt.show()


