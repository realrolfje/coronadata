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

plt.figure(figsize=(10,5))
plt.plot(x,y,label='positief getest')

ax = a[int(avgsize/2):]
xx = x[:len(ax)]
plt.plot(xx,ax,label=str(avgsize)+' daags gemiddelde, -'+str(int(avgsize/2)))
plt.xlabel("Datum")
plt.ylabel("Positief getest per dag")
plt.title('COVID-19 besmettingen, '+filedate)
plt.legend()
plt.savefig("../graphs/besmettingen.png")
#plt.show()
