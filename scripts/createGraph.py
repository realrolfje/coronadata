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
                  for x in range(0, (maxdatum-mindatum).days+7)]
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

positief_voorspeld = {
    'x': [],
    'y': [],
    'avgsize': 12
}

ziek = {
    'x' : [],
    'y' : [],
    'ziekteduur' : 14
}

ic = {
    'x' : [],
    'y' : [],
    'rc' : []
}

ic_voorspeld = {
    'x' : [],
    'y' : [],
    'avgsize': 3
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

    # --------------------------------- Normale grafieken (exclusief data van vandaag want dat is altijd incompleet)
    if datum in metenisweten and parser.parse(datum).date() < datetime.date.today():
        positief['x'].append(parser.parse(datum))
        positief['y'].append(metenisweten[datum]['positief'])

        ic['x'].append(parser.parse(datum))
        ic['y'].append(metenisweten[datum]['nu_op_ic'])

        if len(ic['y'])>1:
            ic['rc'].append(ic['y'][-1] - ic['y'][-2])
        else:
            ic['rc'].append(0)

    # --------------------------------- Gemiddeld positief getest
    if datum in metenisweten:
        avg = mean(positief['y'][len(positief['y'])-11:])
    else:
        avg = mean(positief_gemiddeld['y'][len(positief_gemiddeld['y'])-11:])
    positief_gemiddeld['x'].append(parser.parse(datum) - datetime.timedelta(days=positief_gemiddeld['avgsize']/2))
    positief_gemiddeld['y'].append(avg)

    # ---------------------- Voorspelling positief getst obv gemiddelde richtingscoefficient positief getest.
    if datum in metenisweten and len(positief['y']) > 2 and parser.parse(datum) < (datetime.datetime.now() - datetime.timedelta(days=7)):
        rc = positief['y'][-1]-positief['y'][-2]
    elif len(positief_voorspeld['y']) > 2: 
        rc = positief_voorspeld['y'][-1]-positief_voorspeld['y'][-2]
    else :
        rc = 0
    
    try:
        rc_avg = rc_avg * (positief_voorspeld['avgsize'] - 1) / positief_voorspeld['avgsize'] + rc / positief_voorspeld['avgsize']
    except NameError:
        rc_avg = 0

    try:
        voorspeld_huidig = voorspeld_huidig + rc_avg
    except NameError:
        voorspeld_huidig = 0

    positief_voorspeld['x'].append(parser.parse(datum) - datetime.timedelta(days=positief_voorspeld['avgsize']/2))
    positief_voorspeld['y'].append(voorspeld_huidig)   

    # ---------------------- Voorspelling op IC obv gemiddelde richtingscoefficient positief getest.
    if len(ic['x']) > 10 and parser.parse(datum) > ic['x'][-1]:
        ic_rc = mean(ic['rc'][-5:])

        ic_voorspeld['x'].append(parser.parse(datum))
        ic_voorspeld['y'].append(ic['y'][-1] + ic_rc * (parser.parse(datum) - ic['x'][-1]).days )


    # --------------------------------- Positief getest, en nu ziek (beter na x dagen)
    beterdag = (parser.parse(datum) - datetime.timedelta(days=ziek['ziekteduur'])).strftime("%Y-%m-%d")
    
    if datum in metenisweten and parser.parse(datum) < (datetime.datetime.now() - datetime.timedelta(days=7)):
        ziekgeworden = metenisweten[datum]['positief']
    else :
        ziekgeworden = positief_voorspeld['y'][-1]

    if beterdag in metenisweten and parser.parse(beterdag) < (datetime.datetime.now() - datetime.timedelta(days=7)):
        betergeworden = metenisweten[beterdag]['positief']
    else:
        try:
            betergeworden = positief_voorspeld['y'][len(positief_voorspeld['y']) - ziek['ziekteduur']]
        except IndexError:
            betergeworden = avg
    
    try:
        nuziek = nuziek + ziekgeworden
    except NameError:
        nuziek = ziekgeworden

    if beterdag in metenisweten:
        nuziek = nuziek - betergeworden

    # --- Ziekte niet verder voorspellen dan de besmetting voorspelling
    if parser.parse(datum) < (date_range[-1] - datetime.timedelta(days=positief_voorspeld['avgsize']/2)):
        ziek['x'].append(parser.parse(datum))
        ziek['y'].append(nuziek)


def anotate(plt, metenisweten, datum, tekst, x, y):
    plt.annotate(
        tekst,
        xy=(parser.parse(datum), metenisweten[datum]['positief']),
        xytext=(parser.parse(x), y),
        fontsize=8,
        bbox=dict(boxstyle='round,pad=0.4', fc='ivory', alpha=1),
        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.1')
    )


fig, ax1 = plt.subplots(figsize=(10, 5))
ax2 = plt.twinx()

#plt.figure(figsize =(10,5))
ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)
ax2.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)

# Plot cases per dag
ax1.plot(positief['x'][:-10], positief['y'][:-10], color='steelblue', label='positief getest')
ax1.plot(positief['x'][-11:], positief['y'][-11:], color='steelblue', linestyle='--', alpha=0.2)

anotate(ax1, metenisweten, "2020-03-09",
        'Brabant geen\nhanden schudden', "2020-02-05", 300)
anotate(ax1, metenisweten, "2020-03-15",
        'Onderwijs,\nverpleeghuis,\nhoreca\ndicht', "2020-02-05", 600)
anotate(ax1, metenisweten, "2020-03-23",
        '1,5 meter, €400 boete', "2020-02-05", 1000)
anotate(ax1, metenisweten, "2020-04-22", 'Scholen 50% open', "2020-05-05", 800)
anotate(ax1, metenisweten, "2020-05-11",
        'Scholen,\nkappers,\ntandarts\nopen', "2020-03-28", 50)
anotate(ax1, metenisweten, "2020-06-01", 'Terrassen open,\ntests voor\niedereen', "2020-05-20", 380)
anotate(ax1, metenisweten, "2020-07-01",
        'Maatregelen afgezwakt,\nalleen nog 1,5 meter,\nmondkapje in OV', "2020-06-01", 600)
anotate(ax1, metenisweten, "2020-07-04",
        'Begin\nschoolvakanties', "2020-06-29", 350)

# Plot average per dag
# ax1.plot(positief_gemiddeld['x'], positief_gemiddeld['y'], color='cyan', linestyle=':',
#          label=str(positief_gemiddeld['avgsize'])+' daags gemiddelde, t-' +
#          str(int(positief_gemiddeld['avgsize']/2))
#          )

ax1.plot(positief_voorspeld['x'][-15:], positief_voorspeld['y'][-15:], 
         color='steelblue', linestyle=':')

ax1.plot(ic['x'], ic['y'], color='red', label='aantal op IC (nu: '+str(ic['y'][-1])+')')
ax1.plot(ic_voorspeld['x'], ic_voorspeld['y'], color='red', linestyle=':')

ax2.plot(ziek['x'], ziek['y'], color='darkorange',
         linestyle=':', label='aantal getest ziek')

ax1.set_xlabel("Datum")
ax1.set_ylabel("Positief getest per dag")
ax2.set_ylabel("Aantal zieken")

ax1.set_ylim([0, 1400])
ax2.set_ylim([0, 14000])

plt.gca().set_xlim([parser.parse("2020-02-01"), ic_voorspeld['x'][-1]])

# ax1.set_yscale('log')
# ax2.set_yscale('log')


plt.title('COVID-19 besmettingen, '+filedate)
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")
plt.savefig("../graphs/besmettingen.png")
#plt.show()
