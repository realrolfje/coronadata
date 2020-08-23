#!/usr/bin/env python3
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
from dateutil import parser
from statistics import mean
import datetime
import json
import modules.brondata as brondata

metenisweten = brondata.readjson('../cache/daily-stats.json')

Rt_avg = {    'x':[],    'y':[]}
Rt_low = {    'x':[],    'y':[]}
Rt_up  = {    'x':[],    'y':[]}

for datum in metenisweten:
    if metenisweten[datum]['Rt_avg'] is not None:
        Rt_avg['x'].append(parser.parse(datum))
        Rt_avg['y'].append(metenisweten[datum]['Rt_avg'])
    if metenisweten[datum]['Rt_up'] is not None:
        Rt_up['x'].append(parser.parse(datum))
        Rt_up['y'].append(metenisweten[datum]['Rt_up'])
    if metenisweten[datum]['Rt_low'] is not None:
        Rt_low['x'].append(parser.parse(datum))
        Rt_low['y'].append(metenisweten[datum]['Rt_low'])


def decimalstring(number):
    return "{:,}".format(number).replace(',','.')


plt.figure(figsize=(10,3))
plt.subplots_adjust(bottom=0.12, left=0.09, right=0.91)
plt.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)
plt.plot(Rt_avg['x'], Rt_avg['y'], color='darkgreen', label='Rt_avg')
plt.plot(Rt_up['x'], Rt_up['y'], color='gray', linestyle='--', alpha=0.3)
plt.plot(Rt_low['x'], Rt_low['y'], color='gray', linestyle='--', alpha=0.3)
plt.axhline(1, color='red')

axes = plt.gca()
axes.set_ylim([0,3])
axes.set_xlim([parser.parse("2020-02-01"),datetime.date.today() + datetime.timedelta(days=7)])
axes.set_xlabel("Datum")
axes.set_ylabel("Reproductiegetal")

gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
plt.title('Reproductiegetal, '+gegenereerd_op)

footerleft="Gegenereerd op "+gegenereerd_op+".\nSource code: http://github.com/realrolfje/coronadata"
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")

footerright="Bron: https://data.rivm.nl/covid-19"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

plt.savefig("../graphs/reproductiegetal.png", format="png")
plt.savefig("../graphs/reproductiegetal.svg", format="svg")


