#!/usr/bin/env python3
#
from matplotlib import pyplot as plt
from dateutil import parser
import csv
from datetime import datetime
from datetime import timedelta
from modules.brondata import smooth, double_savgol

pagehits= {
    'x': [],
    'y': []
}

# Get daily hitcounter (max value for that day)
filename = '../data/pagehits.csv'
with open(filename, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            datum = datetime.strptime(row[0],"%Y-%m-%dT%H:%M:%S").date()
            hits = int(row[1])

            i = pagehits['x'].index(datum)
            if i:
                if hits > pagehits['y'][i]:
                    pagehits['y'][i] = hits
            else:
                pagehits['x'].append(datum)
                pagehits['y'].append(hits)

        line_count = line_count + 1
    
dailyhits = {
    'x': [],
    'y': []
}

for i in range(len(pagehits['x'])):
    dailyhits['x'] = pagehits['x'][i]
    if i == 0:
        dailyhits['y'] = pagehits['y'][i]
    else:
        dailyhits['y'] = pagehits['y'][i] - pagehits['y'][i-1]

hitsperuur = [y / 24 for y in dailyhits['y']]
hitsperuur_gem = smooth(hitsperuur)

fig, ax1 = plt.subplots(figsize=(10, 5))
fig.subplots_adjust(top=0.92, bottom=0.13, left=0.09, right=0.91)
ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)
ax1.plot(dailyhits['x'], hitsperuur_gem, color='red', label='Page hits')
ax1.fill_between(pagehits['x'], 0, hitsperuur,facecolor='lightsalmon', alpha=0.3, interpolate=True)

ax1.set_ylim(0,4000)

import matplotlib.dates as mdates
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

# Try to create only 7 tickmarks to prevent overlap
step = (pagehits['x'][-1]-pagehits['x'][0]).days/7
r =  [pagehits['x'][0] + timedelta(days=x*step) for x in range(8)]

ax1.set_xticks(r)

ax1.set_xlabel("Datum")

plt.title('Page hits per uur (gemiddeld ongeveer '+str(int(round(hitsperuur_gem['y'][-1])))+").")

gegenereerd_op=datetime.now().strftime("%Y-%m-%d %H:%M")
footerleft="Gegenereerd op "+gegenereerd_op+"."
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")

footerright="https://realrolfje.github.io/coronadata/"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

plt.savefig("../docs/graphs/pagehits.svg", format="svg")
