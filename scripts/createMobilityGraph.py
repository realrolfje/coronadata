#!/usr/bin/env python3
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
import matplotlib.patches as patches
from dateutil import parser
from statistics import mean
import datetime
import json
import modules.brondata as brondata
from modules.datautil import anotate

brondata.freshdata()
metenisweten = brondata.readjson('../cache/daily-stats.json')
events = brondata.readjson('../data/measures-events.json')

rijden = {
    'x': [],
    'y': []
}

lopen = {
    'x': [],
    'y': []
}

ov = {
    'x': [],
    'y': []
}

date_range = brondata.getDateRange(metenisweten)
for d in date_range:
    datum = d.strftime("%Y-%m-%d")

    if datum not in metenisweten:
        continue

    value = metenisweten[datum]['mobiliteit']['rijden']
    if value:
        rijden['x'].append(parser.parse(datum))
        rijden['y'].append(value)

    value = metenisweten[datum]['mobiliteit']['ov']
    if value:
        ov['x'].append(parser.parse(datum))
        ov['y'].append(value)

    value = metenisweten[datum]['mobiliteit']['lopen']
    if value:
        lopen['x'].append(parser.parse(datum))
        lopen['y'].append(value)


rijden['y'] = brondata.double_savgol(rijden['y'], 1, 13, 1)
#ov['y'] = brondata.smooth(ov['y'])
lopen['y'] = brondata.double_savgol(lopen['y'], 1, 13, 1)

print('Generating mobility graph...')

fig, ax1 = plt.subplots(figsize=(10, 3))
fig.subplots_adjust(bottom=0.2, left=0.09, right=0.91)

ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)

plt.gca().set_xlim([parser.parse("2020-02-01"), date_range[-1]])
ax1.set_ylim([20,190])

ax1.axhline(100, color='black', linestyle='-', linewidth=0.4)

ax1.set_yticks      ([20,  40,60,  80, 100, 120, 140, 160, 180])
#ax2.set_yticklabels([ '100k',  '200k', '300k', '400k', '☠'])


ax1.plot(rijden['x'], rijden['y'], color='coral',label='Rijden (Apple, gemiddeld)')
#ax1.plot(ov['x'], ov['y'], color='orange',label='OV')
ax1.plot(lopen['x'], lopen['y'], color='slateblue', label='Lopen (Apple, gemiddeld)')


for event in events:
    if 'mobiliteit' in event:
        anotate(
            ax1, 
            rijden['x'], rijden['y'],
            event['date'], event['event'], 
            event['mobiliteit'][0], 
            event['mobiliteit'][1]
        )

# laat huidige datum zien met vertikale lijn
ax1.axvline(datetime.date.today(), color='teal', linewidth=0.15)

ax1.set_xlabel("Datum")
ax1.set_ylabel("% t.o.v. 13 januari")


gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
plt.title('Mobiliteit '+gegenereerd_op)

footerleft="Gegenereerd op "+gegenereerd_op+".\nSource code: http://github.com/realrolfje/coronadata"
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")

footerright="Bron: https://covid19.apple.com/mobility"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

ax1.legend(loc="upper left")
#ax2.legend(loc="upper right")
plt.savefig("../docs/graphs/mobiliteit.svg", format="svg")
# plt.savefig("../docs/graphs/mobiliteit.png", format="png", dpi=180/2)
# plt.show()
