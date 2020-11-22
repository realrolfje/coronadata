#!/usr/bin/env python3
#
from matplotlib import pyplot as plt
from dateutil import parser
import datetime
import csv
from datetime import datetime

pagehits= {
    'x': [],
    'y': []
}

filename = '../data/pagehits.csv'
with open(filename, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            datum = datetime.strptime(row[0],"%Y-%m-%dT%H:%M:%S")
            hits = int(row[1])
            
            if len(pagehits['x']) > 0:
                seconds = (datum - pagehits['x'][-1]).seconds
                deltahits = (hits - pagehits['y'][-1])/seconds
            else:
                deltahits = 0

            pagehits['x'].append(datum)
            pagehits['y'].append(deltahits)
        line_count = line_count + 1
    
fig, ax1 = plt.subplots(figsize=(10, 5))
fig.subplots_adjust(top=0.92, bottom=0.13, left=0.09, right=0.91)
ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)
ax1.plot(pagehits['x'], 
         [x * 3600 for x in pagehits['y']], 
         color='red', label='Page hits')

ax1.set_ylim(0)

import matplotlib.dates as mdates
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

plt.title('Bezoekers per uur')

gegenereerd_op=datetime.now().strftime("%Y-%m-%d %H:%M")
footerleft="Gegenereerd op "+gegenereerd_op+"."
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")

footerright="https://realrolfje.github.io/coronadata/"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

plt.savefig("../docs/graphs/pagehits.svg", format="svg")
