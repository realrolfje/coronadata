#!/usr/bin/env python3 
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
from dateutil import parser
import datetime
import json 

with open('../cache/COVID-19_casus_landelijk.json', 'r') as json_file:
    data = json.load(json_file)
    metenisweten = { }
    for record in data:
        if (record['Date_statistics'] not in metenisweten):
            metenisweten[record['Date_statistics']] = {
                'positief': 0,
            }
        metenisweten[record['Date_statistics']]['positief'] += 1
        filedate = record['Date_file']

x = []
y = []
a = []
avg = 0
avgsize = 14

for datum in metenisweten:
    x.append(parser.parse(datum))
    y.append(metenisweten[datum]['positief'])

    avg = (avg * (avgsize-1) /avgsize) + (metenisweten[datum]['positief'] / avgsize)
    a.append(avg)


def anotate(plt, metenisweten, datum, tekst, x, y):
    plt.annotate(
        tekst, 
        xy=(parser.parse(datum), metenisweten[datum]['positief']),
        xytext=(parser.parse(x), y),
        bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
        arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0')
    )



plt.figure(figsize=(10,5))
plt.grid(which='both', axis='both', linestyle='--', color='gray', linewidth=1, alpha=0.5)

# Plot cases per dag
plt.plot(x,y,label='positief getest')

anotate(plt, metenisweten, "2020-03-09", 'Brabant geen\nhanden schudden', "2020-01-20", 300)
anotate(plt, metenisweten, "2020-03-15", 'Onderwijs\nverpleeghuis\nhoreca\ndicht', "2020-02-01", 800)
anotate(plt, metenisweten, "2020-03-23", '1,5 meter, €400 boete', "2020-01-15", 1150)
anotate(plt, metenisweten, "2020-04-22", 'Scholen 50% open', "2020-04-30", 700)
anotate(plt, metenisweten, "2020-05-11", 'Scholen, kapers,\ntandarts open', "2020-05-11", 450)
anotate(plt, metenisweten, "2020-06-01", 'Terassen open', "2020-05-25", 300)
anotate(plt, metenisweten, "2020-07-01", 'Maatregelen afgezwakt\nAlleen nog 1,5 meter\nmondkapje in OV', "2020-06-25", 450)

# Plot average per dag
ax = a[int(avgsize/2):]
xx = x[:len(ax)]
plt.plot(xx,ax,label=str(avgsize)+' daags gemiddelde, -'+str(int(avgsize/2)))

plt.xlabel("Datum")
plt.ylabel("Positief getest per dag")
plt.title('COVID-19 besmettingen, '+filedate)
plt.legend()
plt.savefig("../graphs/besmettingen.png")
#plt.show()
