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

for datum in metenisweten:
    x.append(parser.parse(datum))
    y.append(metenisweten[datum]['positief'])

plt.plot(x,y)
plt.xlabel("Datum")
plt.ylabel("Positief getest per dag")
plt.title('COVID-19 besmettingen, '+filedate)
plt.savefig("../graphs/besmettingen.png")
#plt.show()
