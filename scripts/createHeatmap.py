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

print("Generating date/age heatmap.")

xlabels = []
x = []
y = []

startdate = parser.parse('2020-02-01')

weightsmap={}

with open('../cache/COVID-19_casus_landelijk.json', 'r') as json_file:
    data = json.load(json_file)
    for record in data:
        try:
            # datax = np.datetime64(record['Date_statistics'])
            datax = (parser.parse(record['Date_statistics']) - startdate).days
            labelx = parser.parse(record['Date_statistics']).date()
            datay = int(record['Agegroup'].split('-')[0].split('+')[0])+5
            filedate = record['Date_file']
            xlabels.append(labelx)
            x.append(datax)
            y.append(datay)

            if datax not in weightsmap:
                weightsmap[datax] = 1
            else:
                weightsmap[datax] = weightsmap[datax] + 1

        except ValueError:
            # print('ERROR '+record['Date_statistics'] + ' | ' + record['Agegroup'])
            pass

weights=[]
for d in x:
    weights.append(1./weightsmap[d])


def decimalstring(number):
    return "{:,}".format(number).replace(',', '.')

gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

plt.figure(figsize=(10,3))
plt.title('Besmettingen per leeftijdsgroep, '+gegenereerd_op)
plt.subplots_adjust(bottom=0.2, left=0.09, right=0.91)

# Gewogen:
#plt.hist2d(x, y, bins=[50,10], range=[[0,x[-1]+7],[0,100]], cmap='inferno', weights=weights)

# Ongewogen:
plt.hist2d(x, y, bins=[200,10], range=[[0,x[-1]+7],[0,100]], cmin=1, cmap='Blues') # inferno is also a good one

plt.ylabel('Leeftijd')
plt.xlabel('Datum') 

# Dirty stuff to get x labels (needs cleanup)
xlabeldates = [startdate + relativedelta(months=x) for x in range(xlabels[-1].month - startdate.month + 1)]
xlabels = []
xlocs = []
for label in xlabeldates:
    xlabels.append(label.strftime("%Y-%m"))
    xlocs.append((label - startdate).days)
locs, labels = plt.xticks(xlocs, xlabels)

# laat huidige datum zien met vertikale lijn
plt.axvline(x[-1], color='teal', linewidth=0.15)

footerleft="Gegenereerd op "+gegenereerd_op+".\nSource code: http://github.com/realrolfje/coronadata"
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")

footerright="Publicatiedatum RIVM "+filedate+".\nBron: https://data.rivm.nl/covid-19"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

plt.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)


plt.savefig("../graphs/besmettingen-leeftijd.png", format="png")
plt.savefig("../graphs/besmettingen-leeftijd.svg", format="svg")

# plt.show()


