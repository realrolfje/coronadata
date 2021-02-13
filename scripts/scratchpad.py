#!/usr/bin/env python3
#
from matplotlib import pyplot as plt
from dateutil import parser
from statistics import mean
import datetime
import csv
import json
import modules.brondata as brondata
from modules.brondata import decimalstring, smooth
from scipy.ndimage.filters import uniform_filter1d
from operator import itemgetter
import urllib.request
import re
from datetime import datetime

brondata.freshdata()
metenisweten = brondata.readjson('../cache/daily-stats.json')
events = brondata.readjson('../data/measures-events.json')

vaccins_totaal = {
    'x': [],
    'astra_zeneca': [],
    'pfizer': [],
    'cure_vac': [],
    'janssen': [],
    'moderna': [],
    'sanofi': [],
    'totaal': []
}

date_range = brondata.getDateRange(metenisweten)


def addVaccinCount(record, vaccin):
    if (len(vaccins_totaal[vaccin]) > 0):
        vaccins_totaal[vaccin].append(
            vaccins_totaal[vaccin][-1] + record[vaccin]
        )
    else:
        vaccins_totaal[vaccin].append(record[vaccin])
    return record[vaccin]


for d in date_range:
    datum = d.strftime("%Y-%m-%d")
    if (datum in metenisweten and metenisweten[datum]['vaccinaties']['astra_zeneca'] != None):
        vaccins_totaal['x'].append(datum)

        record = metenisweten[datum]['vaccinaties']
        daytotal = addVaccinCount(record, 'astra_zeneca')\
            + addVaccinCount(record, 'pfizer')\
            + addVaccinCount(record, 'cure_vac')\
            + addVaccinCount(record, 'janssen')\
            + addVaccinCount(record, 'moderna')\
            + addVaccinCount(record, 'sanofi')

        if (len(vaccins_totaal['totaal']) > 0):
            vaccins_totaal['totaal'].append(
                vaccins_totaal['totaal'][-1] + daytotal
            )
        else:
            vaccins_totaal['totaal'].append(daytotal)

print('Generating vaccination graph...')
fig, ax1 = plt.subplots(figsize=(10, 5))
fig.subplots_adjust(top=0.92, bottom=0.13, left=0.09, right=0.91)

ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)

ax1.set_xlabel("Datum")
ax1.set_ylabel("Aantal gevaccineerd")


ax1.stackplot(
    vaccins_totaal['x'],
    [x/2 for x in vaccins_totaal['astra_zeneca']],
    [x/2 for x in vaccins_totaal['pfizer']],
    [x/2 for x in vaccins_totaal['cure_vac']],
    [x/2 for x in vaccins_totaal['janssen']],
    [x/2 for x in vaccins_totaal['moderna']],
    [x/2 for x in vaccins_totaal['sanofi']],
    labels=(
        'COVID-19 Vaccine AstraZeneca ®',
        'Comirnaty® (BioNTech/Pfizer)',
        'CVnCoV (CureVac)',
        'janssen',
        'COVID-19 Vaccine Moderna ®',
        'Sanofi/GSK'
    ),
    baseline='zero'
)


# Let op! Mensen hebben van (de meeste) vaccins twee prikken nodig.
# Dat betekent dat de dashboard data van RIVM ongelofelijk slecht is.
# Omdat we niet weten hoeveel mensen 1x of 2x zijn ingeent, nemen we
# hier even aan dat alle vaccins 2 prikken nodig hebben, EN dat
# die dan  ook bij 1 persoon zijn gezet (dat betekent grofweg dat de data
# van 3 weken terug beter klopt dan de data van vorige week)
totaal_complete_vaccins = decimalstring(vaccins_totaal['totaal'][-1]/2)
percentage_complete_vaccins = decimalstring(
    round((100*vaccins_totaal['totaal'][-1]/2)/17500000, 2))

ax1.plot(vaccins_totaal['x'], [x/2 for x in vaccins_totaal['totaal']], color='black',
         label='Totaal (nu: ' + totaal_complete_vaccins + ', ' + percentage_complete_vaccins + '%)')

ax1.legend(loc="upper left")


plt.savefig("../docs/graphs/vaccinaties.svg", format="svg")
