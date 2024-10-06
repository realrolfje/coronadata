#!/usr/bin/env python3
#
# pip3 install matplotlib

import sys
from matplotlib import pyplot as plt
import datetime
import modules.brondata as brondata
import modules.arguments as arguments
from modules.brondata import decimalstring, dateCache
from modules.datautil import runIfNewData

def main():
    runIfNewData(__file__)
    metenisweten = brondata.readjson('../data/daily-stats.json')
    createRtraph(metenisweten)

def createRtraph(metenisweten):
    date_range = brondata.getDateRange(metenisweten)

    lastDays = arguments.lastDays()
    if (lastDays>0):
        date_range = date_range[-lastDays:]

    print('Generating Rt graph...')

    Rt_avg = {    'x':[],    'y':[]}
    Rt_low = {    'x':[],    'y':[]}
    Rt_up  = {    'x':[],    'y':[]}

    for d in date_range:
        datum = d.strftime("%Y-%m-%d")

        if datum in metenisweten and metenisweten[datum]['Rt_avg'] is not None:
            Rt_avg['x'].append(dateCache.parse(datum))
            Rt_avg['y'].append(float(metenisweten[datum]['Rt_avg']))
        if datum in metenisweten and metenisweten[datum]['Rt_up'] is not None:
            Rt_up['x'].append(dateCache.parse(datum))
            Rt_up['y'].append(float(metenisweten[datum]['Rt_up']))
        if datum in metenisweten and metenisweten[datum]['Rt_low'] is not None:
            Rt_low['x'].append(dateCache.parse(datum))
            Rt_low['y'].append(float(metenisweten[datum]['Rt_low']))


    plt.figure(figsize=(10,3))
    plt.subplots_adjust(bottom=0.2, left=0.09, right=0.91)
    plt.grid(which='both', axis='both', linestyle='-.',
            color='gray', linewidth=1, alpha=0.3)
    plt.plot(Rt_avg['x'], Rt_avg['y'], color='black', label='Rt_avg')
    plt.plot(Rt_up['x'], Rt_up['y'], color='gray', linestyle='--', alpha=0.3)
    plt.plot(Rt_low['x'], Rt_low['y'], color='gray', linestyle='--', alpha=0.3)


    high = []
    low = []
    for val in Rt_avg['y']:
        if val > 1:
            high.append(True)
            low.append(False)
        else:
            high.append(False)
            low.append(True)

    plt.fill_between(Rt_avg['x'], 1, Rt_avg['y'], where=high, facecolor='red', alpha=0.3, interpolate=True)
    plt.fill_between(Rt_avg['x'], 1, Rt_avg['y'], where=low, facecolor='green',  alpha=0.3, interpolate=True)

    # Put vertical line at current day
    plt.text(
        x=dateCache.today(),
        y=0,
        s=datetime.datetime.now().strftime("%d"), 
        color="white",
        fontsize=8,
        ha="center",
        va="center",
        bbox=dict(boxstyle='round,pad=0.1', facecolor='red', alpha=1, edgecolor='red'),
        zorder=10
    )
    plt.axvline(dateCache.today(), color='red', linewidth=0.5)

    # Laat afkappunt R zien (is twee weken geleden)
    plt.axvline(dateCache.today() - datetime.timedelta(days=14), color='blue', linestyle='--', linewidth=0.5)

    if len(Rt_avg['y']) > 1 and len(Rt_avg['x']) > 1:
        plt.annotate(
            decimalstring(Rt_avg['y'][-1]),
            xy=(Rt_avg['x'][-1], Rt_avg['y'][-1]),
            xytext=(Rt_avg['x'][-1], Rt_avg['y'][-1]+0.5),
            fontsize=8,
            bbox=dict(boxstyle='round,pad=0.4', fc='ivory', alpha=1),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.1')
        )

    axes = plt.gca()
    axes.set_ylim([0,3])
    axes.set_xlim([date_range[0],date_range[-1]])
    axes.set_xlabel("Datum")
    axes.set_ylabel("Reproductiegetal")

    gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    plt.title('Reproductiegetal')

    if len(Rt_avg['x']) > 1:
        R_op=Rt_avg['x'][-1].strftime("%Y-%m-%d")
    else: R_op = "onbekend"

    footerleft="Gegenereerd op "+gegenereerd_op+", Rt berekend tot "+R_op+".\nSource code: http://github.com/realrolfje/coronadata"
    plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")

    footerright="Bron: https://data.rivm.nl/covid-19"
    plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

    if (lastDays > 0):
        filename = "../docs/graphs/reproductiegetal-"+str(lastDays)+".svg"
    else:
        filename = "../docs/graphs/reproductiegetal.svg"

    print(f"Saving {filename}")
    plt.savefig(filename, format="svg")
        
    dateCache.cacheReport()

if __name__ == '__main__':
    sys.exit(main())