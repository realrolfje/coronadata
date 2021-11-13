#!/usr/bin/env python3
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
from dateutil import parser
import datetime
import modules.arguments as arguments
import modules.brondata as brondata
from modules.datautil import anotate

print("------------ %s ------------" % __file__)
if (brondata.freshdata() or brondata.isnewer(__file__, '../cache/daily-stats.json') or arguments.isForce()):
    print("New data, regenerate output.")
else:
    print("No fresh data, and unchanged code. Exit.")
    exit(0)

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
lastDays = arguments.lastDays()
if (lastDays>0):
    date_range = date_range[-lastDays:]


for d in date_range:
    datum = d.strftime("%Y-%m-%d")

    if datum not in metenisweten:
        continue

    value = metenisweten[datum]['mobiliteit']['rijden']
    if value:
        rijden['x'].append(parser.parse(datum))
        rijden['y'].append(value)

    if 'OV' in metenisweten[datum]['mobiliteit']:
        value = metenisweten[datum]['mobiliteit']['OV']
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

fig, ax1 = plt.subplots(figsize=(10, 4))
fig.subplots_adjust(top=0.92, bottom=0.17, left=0.09, right=0.91)

ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)

plt.gca().set_xlim([date_range[0], date_range[-1]])
ax1.set_ylim([0,190])

ax1.axhline(100, color='black', linestyle='-', linewidth=0.4)

ax1.set_yticks      ([0, 20,  40, 60,  80, 100, 120, 140, 160, 180])
#ax2.set_yticklabels([ '100k',  '200k', '300k', '400k', '☠'])


ax1.plot(rijden['x'], rijden['y'], color='coral',label='Rijden (Apple, gemiddeld)')
ax1.plot(ov['x'], ov['y'], color='lightgreen',label='OV (Apple, gemiddeld)')
ax1.plot(lopen['x'], lopen['y'], color='slateblue', label='Lopen (Apple, gemiddeld)')


for event in events:
    if 'mobiliteit' in event and parser.parse(event['mobiliteit'][0]) > date_range[0]:
        anotate(
            ax1, 
            rijden['x'], rijden['y'],
            event['date'], event['event'], 
            event['mobiliteit'][0], 
            event['mobiliteit'][1]
        )

# Put vertical line at current day
plt.text(
    x=datetime.date.today(),
    y=0,
    s=datetime.datetime.now().strftime("%d"), 
    color="red",
    fontsize=8,
    ha="center",
    va="center",
    bbox=dict(facecolor='yellow', alpha=0.9, pad=0, edgecolor='yellow'),
    zorder=10
)
plt.axvline(datetime.date.today(), color='red', linewidth=0.5)

ax1.set_xlabel("Datum")
ax1.set_ylabel("% t.o.v. 13 januari 2021")

gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
plt.title('Mobiliteit (op basis van reisplanningsverzoeken)')

data_tot=rijden['x'][-1].strftime("%Y-%m-%d")
footerleft="Gegenereerd op "+gegenereerd_op+", o.b.v. data tot "+data_tot+".\nSource code: http://github.com/realrolfje/coronadata"
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")

footerright="Bron: https://covid19.apple.com/mobility"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

ax1.legend(loc="upper left")
#ax2.legend(loc="upper right")

if (lastDays > 0):
    plt.savefig("../docs/graphs/mobiliteit-"+str(lastDays)+".svg", format="svg")
else:
    plt.savefig("../docs/graphs/mobiliteit.svg", format="svg")
