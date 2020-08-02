#!/usr/bin/env python3 
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
from dateutil import parser
import datetime
import json 

print("Generating graphs.")

with open('../cache/COVID-19_casus_landelijk.json', 'r') as json_file:
    data = json.load(json_file)
    metenisweten = { }
    for record in data:
        if (record['Date_statistics'] not in metenisweten):
            metenisweten[record['Date_statistics']] = {
                'positief': 0,
                'nu_op_ic': 0
            }
        metenisweten[record['Date_statistics']]['positief'] += 1
        filedate = record['Date_file']

with open('../cache/NICE-intake-count.json', 'r') as json_file:
    data = json.load(json_file)
    for measurement in data:
        if (measurement['date'] not in metenisweten):
            metenisweten[measurement['date']] = {
                'positief': 0,
                'nu_op_ic': 0
            }
        metenisweten[measurement['date']]['nu_op_ic'] += measurement['value']

x = []
y = []

a = []
avg = 0
avgsize = 14

z = []
ziek = 0
ziekteduur = 14

i = []

# print("2020-01-30")
# print((parser.parse("2020-01-30") - datetime.timedelta(days=ziekteduur)).strftime("%Y-%m-%d"))
# exit

for datum in metenisweten:
    x.append(parser.parse(datum))
    y.append(metenisweten[datum]['positief'])
    i.append(metenisweten[datum]['nu_op_ic']*10)
   
    avg = (avg * (avgsize-1) /avgsize) + (metenisweten[datum]['positief'] / avgsize)
    a.append(avg)

    beterdag = (parser.parse(datum) - datetime.timedelta(days=ziekteduur)).strftime("%Y-%m-%d")
    ziek = ziek + metenisweten[datum]['positief']
    if beterdag in metenisweten:
        ziek = ziek - metenisweten[beterdag]['positief']
    z.append(ziek)



def anotate(plt, metenisweten, datum, tekst, x, y):
    plt.annotate(
        tekst, 
        xy=(parser.parse(datum), metenisweten[datum]['positief']),
        xytext=(parser.parse(x), y),
        bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
        arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0')
    )

fig, ax1 = plt.subplots(figsize=(10,5))
ax2 = plt.twinx()

#plt.figure(figsize =(10,5))
ax1.grid(which='both', axis='both', linestyle='-.', color='gray', linewidth=1, alpha=0.3)
ax2.grid(which='both', axis='both', linestyle='-.', color='gray', linewidth=1, alpha=0.3)

# Plot cases per dag
ax1.plot(x,y,label='positief getest')

anotate(ax1, metenisweten, "2020-03-09", 'Brabant geen\nhanden schudden', "2020-01-20", 300)
anotate(ax1, metenisweten, "2020-03-15", 'Onderwijs\nverpleeghuis\nhoreca\ndicht', "2020-02-01", 600)
anotate(ax1, metenisweten, "2020-03-23", '1,5 meter, €400 boete', "2020-01-15", 1000)
anotate(ax1, metenisweten, "2020-04-22", 'Scholen 50% open', "2020-04-25", 900)
anotate(ax1, metenisweten, "2020-05-11", 'Scholen, kapers,\ntandarts open', "2020-05-08", 500)
anotate(ax1, metenisweten, "2020-06-01", 'Terassen open', "2020-05-25", 310)
anotate(ax1, metenisweten, "2020-07-01", 'Maatregelen afgezwakt\nAlleen nog 1,5 meter\nmondkapje in OV', "2020-06-20", 550)

# Plot average per dag
ax = a[int(avgsize/2):]
xx = x[:len(ax)]
ax1.plot(xx,ax,color='cyan', linestyle=':', label=str(avgsize)+' daags gemiddelde, t-'+str(int(avgsize/2)))

ax2.plot(x,z,color='orange', linestyle=':', label='aantal getest ziek')
ax2.plot(x,i,color='red', label='aantal nu op IC (*10)')

ax1.set_xlabel("Datum")
ax1.set_ylabel("Positief getest per dag")
ax2.set_ylabel("Aantal zieken")

ax1.set_ylim([0, 1400])
ax2.set_ylim([0, 14000])

plt.title('COVID-19 besmettingen, '+filedate)
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")
plt.savefig("../graphs/besmettingen.png")
#plt.show()
