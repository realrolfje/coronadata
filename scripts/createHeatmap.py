#!/usr/bin/env python3
#
# pip3 install matplotlib

import numpy as np
from matplotlib import pyplot as plt
from dateutil import parser
from statistics import mean
import datetime
import json

print("Generating date/age heatmap.")

xlabels = []
x = []
y = []

startdate = parser.parse('2020-02-01')

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
        except ValueError:
            # print('ERROR '+record['Date_statistics'] + ' | ' + record['Agegroup'])
            pass


def decimalstring(number):
    return "{:,}".format(number).replace(',', '.')

gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

plt.figure(figsize=(10,5))
plt.title('Besmettingen per leeftijdsgroep, '+gegenereerd_op)
plt.hist2d(x, y, bins=[50,10], range=[[0,x[-1]],[0,100]])
plt.ylabel('leeftijd')
plt.xlabel('dagen sinds 2020-02-01') 

# Figure out how to get dates on the x axes
# (fig, ax) = plt.subplots()
# ax.set_xlabels(xlabels)

footerleft="Gegenereerd op "+gegenereerd_op+".\nSource code: http://github.com/realrolfje/coronadata"
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")

footerright="Publicatiedatum RIVM "+filedate+".\nBron: https://data.rivm.nl/covid-19"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

plt.grid(which='both', axis='both', color='gray', linewidth=1, alpha=0.5)

plt.savefig("../graphs/besmettingen-leeftijd.png", format="png")
plt.savefig("../graphs/besmettingen-leeftijd.svg", format="svg")

# plt.show()




# plt.show()


