#!/usr/bin/env python3
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
from dateutil import parser
from statistics import mean
import datetime
import json


def getDateRange(metenisweten):
    for datum in metenisweten:
        try:
            mindatum
        except NameError:
            mindatum = parser.parse(datum)

        try:
            maxdatum
        except NameError:
            maxdatum = parser.parse(datum)

        mindatum = min(mindatum, parser.parse(datum))
        maxdatum = max(maxdatum, parser.parse(datum))

    date_range = [mindatum + datetime.timedelta(days=x)
                  for x in range(0, (maxdatum-mindatum).days+30)]
    return date_range


print("Generating graphs.")

with open('../cache/COVID-19_casus_landelijk.json', 'r') as json_file:
    data = json.load(json_file)
    metenisweten = {}
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

positief = {
    'x': [],
    'y': []
}

positief_gemiddeld = {
    'x': [],
    'y': [],
    'avgsize': 14
}

ziek = {
    'x' : [],
    'y' : [],
    'ziekteduur' : 14
}

ic = {
    'x' : [],
    'y' : [],
    'scale' : 10
}

besmettingsgraad = {
    'x' : [],
    'y' : []    
}

# print("2020-01-30")
# print((parser.parse("2020-01-30") - datetime.timedelta(days=ziekteduur)).strftime("%Y-%m-%d"))
# exit

date_range = getDateRange(metenisweten)

for d in date_range:
    datum = d.strftime("%Y-%m-%d")

    if datum in metenisweten:
        positief['x'].append(parser.parse(datum))
        positief['y'].append(metenisweten[datum]['positief'])

        ic['x'].append(parser.parse(datum))
        ic['y'].append(metenisweten[datum]['nu_op_ic'] * ic['scale'])  # <-------------- Let op! Scaled!

    if datum in metenisweten:
        avg = mean(positief['y'][len(positief['y'])-11:])
    else:
        avg = mean(positief_gemiddeld['y'][len(positief_gemiddeld['y'])-11:])
    positief_gemiddeld['x'].append(parser.parse(datum) - datetime.timedelta(days=positief_gemiddeld['avgsize']/2))
    positief_gemiddeld['y'].append(avg)

    beterdag = (parser.parse(datum) - datetime.timedelta(days=ziek['ziekteduur'])).strftime("%Y-%m-%d")
    
    if datum in metenisweten:
        ziekgeworden = metenisweten[datum]['positief']
    else :
        ziekgeworden = avg

    if beterdag in metenisweten:
        betergeworden = metenisweten[beterdag]['positief']
    else:
        try:
            betergeworden = positief_gemiddeld['y'][len(positief_gemiddeld['y']) - ziek['ziekteduur']]
        except IndexError:
            betergeworden = avg
    
    try:
        nuziek = nuziek + ziekgeworden
    except NameError:
        nuziek = ziekgeworden

    if beterdag in metenisweten:
        nuziek = nuziek - betergeworden

    ziek['x'].append(parser.parse(datum))
    ziek['y'].append(nuziek)

    


def anotate(plt, metenisweten, datum, tekst, x, y):
    plt.annotate(
        tekst,
        xy=(parser.parse(datum), metenisweten[datum]['positief']),
        xytext=(parser.parse(x), y),
        bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0')
    )


fig, ax1 = plt.subplots(figsize=(10, 5))
ax2 = plt.twinx()

#plt.figure(figsize =(10,5))
ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)
ax2.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)

# Plot cases per dag
ax1.plot(positief['x'], positief['y'], label='positief getest')

anotate(ax1, metenisweten, "2020-03-09",
        'Brabant geen\nhanden schudden', "2020-01-20", 300)
anotate(ax1, metenisweten, "2020-03-15",
        'Onderwijs\nverpleeghuis\nhoreca\ndicht', "2020-02-01", 600)
anotate(ax1, metenisweten, "2020-03-23",
        '1,5 meter, €400 boete', "2020-01-15", 1000)
anotate(ax1, metenisweten, "2020-04-22", 'Scholen 50% open', "2020-04-25", 900)
anotate(ax1, metenisweten, "2020-05-11",
        'Scholen, kapers,\ntandarts open', "2020-05-08", 500)
anotate(ax1, metenisweten, "2020-06-01", 'Terassen open', "2020-05-25", 310)
anotate(ax1, metenisweten, "2020-07-01",
        'Maatregelen afgezwakt\nAlleen nog 1,5 meter\nmondkapje in OV', "2020-06-20", 550)

# Plot average per dag
ax1.plot(positief_gemiddeld['x'], positief_gemiddeld['y'], color='cyan', linestyle=':',
         label=str(positief_gemiddeld['avgsize'])+' daags gemiddelde, t-' +
         str(int(positief_gemiddeld['avgsize']/2))
         )

ax2.plot(ziek['x'], ziek['y'], color='orange',
         linestyle=':', label='aantal getest ziek')
ax2.plot(ic['x'], ic['y'], color='red', label='aantal nu op IC (*'+str(ic['scale'])+')')

ax1.set_xlabel("Datum")
ax1.set_ylabel("Positief getest per dag")
ax2.set_ylabel("Aantal zieken")

ax1.set_ylim([0, 1400])
ax2.set_ylim([0, 14000])

# ax1.set_yscale('log')
# ax2.set_yscale('log')


plt.title('COVID-19 besmettingen, '+filedate)
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")
plt.savefig("../graphs/besmettingen.png")
plt.show()
