#!/usr/bin/env python3
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
from dateutil import parser
import modules.brondata as brondata
from modules.brondata import decimalstring

print("------------ %s ------------" % __file__)
if not (brondata.freshdata() or brondata.isnewer(__file__, '../cache/daily-stats.json')):
    print("No fresh data, and unchanged code. Exit.")
    exit(0)
else:
    print("New data, regenerate output.")

metenisweten = brondata.readjson('../cache/daily-stats.json')

alpha = {
    'x': [],
    'y': []
}

beta = {
    'x': [],
    'y': []
}

gamma = {
    'x': [],
    'min': [],
    'max': []
}

Rt = None

for datum in metenisweten:
    # if metenisweten[datum]['RNA_per_ml_avg']:
    #     alpha['x'].append(parser.parse(datum))
    #     alpha['y'].append(metenisweten[datum]['RNA_per_ml_avg'])

    if metenisweten[datum]['rivm_schatting_besmettelijk']['value']:
        alpha['x'].append(parser.parse(datum))
        alpha['y'].append(metenisweten[datum]
                          ['rivm_schatting_besmettelijk']['value'])

    if metenisweten[datum]['rolf_besmettelijk']:
        beta['x'].append(parser.parse(datum))
        beta['y'].append(metenisweten[datum]['rolf_besmettelijk'])

    if metenisweten[datum]['Rt_avg']:
        Rt = float(metenisweten[datum]['Rt_avg'])

print('Generating live iphone icon mini graph...')

fig, ax1 = plt.subplots(figsize=(2, 2))
fig.subplots_adjust(top=1, bottom=0, left=0, right=1)

ax = plt.gca()
ax.axes.xaxis.set_visible(False)
ax.axes.yaxis.set_visible(False)

mx = max(max(alpha['y']),max(beta['y']))
mx = mx * 1.4 + mx * 0.2
ax1.set_ylim([-mx*0.2, mx])

plt.figtext(0.5, 0.80,
            "\n           CORONADATA           ",
            color="black",
            fontsize='xx-large',
            horizontalalignment='center',
            fontweight='bold',
            bbox=dict(
                facecolor='yellow', 
                edgecolor='yellow',
                alpha=1.0,
            ),
            zorder=10)

plt.figtext(0.5, 0.02,
            "Rt="+decimalstring(Rt),
            color="royalblue",
            fontsize=20,
            fontweight='extra bold',
            horizontalalignment='center',
            # verticalalignment='center',
            alpha=0.5,
            zorder=10)


ax1.plot(alpha['x'], alpha['y'], color='lightblue')
ax1.plot(beta['x'], beta['y'], color='red')

plt.setp(ax1.spines.values(), color='white')

plt.savefig("../docs/icons/apple-touch-icon.svg", format="svg")
plt.savefig("../docs/icons/apple-touch-icon.png", format="png", dpi=180/2)
