#!/usr/bin/env python3
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
from dateutil import parser
from statistics import mean
import datetime
import json
import modules.brondata as brondata
from modules.brondata import decimalstring
from modules.datautil import anotate


brondata.freshdata()
metenisweten = brondata.readjson('../cache/daily-stats.json')
events = brondata.readjson('../data/measures-events.json')


print("Calculating predictions...")

personen_positief = {
    'x': [],
    'y': []
}

positief = {
    'x': [],
    'y': []
}

positief_voorspeld = {
    'x': [],
    'y': [],
    'avgsize':12
}

totaaltests = {
    'x': [],
    'y': []
}

positief_percentage = {
    'x': [],
    'y': []
}

date_range = brondata.getDateRange(metenisweten)

for d in date_range:
    datum = d.strftime("%Y-%m-%d")

    # --------------------------------- Normale grafieken (exclusief data van vandaag want dat is altijd incompleet)
    if datum in metenisweten and parser.parse(datum).date() <= (datetime.date.today()):
        positief['x'].append(parser.parse(datum))
        positief['y'].append(metenisweten[datum]['positief'])

        if metenisweten[datum]['rivm_totaal_personen_positief']:
            personen_positief['x'].append(parser.parse(datum))
            personen_positief['y'].append(metenisweten[datum]['rivm_totaal_personen_positief'])

        if metenisweten[datum]['rivm_totaal_personen_getest']:
            totaaltests['x'].append(parser.parse(datum))
            totaaltests['y'].append(metenisweten[datum]['rivm_totaal_personen_getest'])

        if metenisweten[datum]['rivm_totaal_personen_getest'] and metenisweten[datum]['rivm_totaal_personen_positief']:
            positief_percentage['x'].append(parser.parse(datum))
            positief_percentage['y'].append(100 * metenisweten[datum]['rivm_totaal_personen_positief'] / metenisweten[datum]['rivm_totaal_personen_getest'])

    if datum in metenisweten:
        totaal_positief = metenisweten[datum]['totaal_positief']

        if metenisweten[datum]['rivm-datum']:
            filedate = metenisweten[datum]['rivm-datum']

    # ---------------------- Voorspelling positief getst obv gemiddelde richtingscoefficient positief getest.
    if datum in metenisweten and len(positief['y']) > positief_voorspeld['avgsize'] and parser.parse(datum) < (datetime.datetime.now() - datetime.timedelta(days=positief_voorspeld['avgsize'])):
        # Voorspel morgen op basis van metingen
        rc = (positief['y'][-1]-positief['y'][-positief_voorspeld['avgsize']]) / positief_voorspeld['avgsize']
        positief_voorspeld['x'].append(parser.parse(datum) + datetime.timedelta(days=1))
        positief_voorspeld['y'].append(positief['y'][-1] + rc)
    elif len(positief_voorspeld['y']) > positief_voorspeld['avgsize']:
        # Voorspel morgen op basis van schatting gisteren
        rc = (positief_voorspeld['y'][-1]-positief_voorspeld['y'][-positief_voorspeld['avgsize']]) / positief_voorspeld['avgsize']
        positief_voorspeld['x'].append(parser.parse(datum) + datetime.timedelta(days=1))
        positief_voorspeld['y'].append(positief_voorspeld['y'][-1] + rc)
    else:
        # If all else fails neem waarde van vorige positief
        positief_voorspeld['x'].append(parser.parse(datum) + datetime.timedelta(days=1))
        positief_voorspeld['y'].append(positief['y'][-1])

print('Generating daily positive tests graph...')

fig, ax1 = plt.subplots(figsize=(10, 5))
fig.subplots_adjust(top=0.92, bottom=0.13, left=0.09, right=0.91)

ax2 = plt.twinx()

ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)
ax2.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)

ax1.text(parser.parse("2020-05-01"), 26000, "Geen smoesjes, je weet het best.\nAls je niet ziek wordt, hoef je ook niet getest.", color="gray")


ax1.plot(totaaltests['x'], totaaltests['y'], 
         color='darkblue', linestyle='-', label='Personen getest')

ax1.plot(personen_positief['x'], personen_positief['y'], 
         color='dodgerblue', linestyle='-', label='Personen positief')

huidigpercentage = decimalstring(round(positief_percentage['y'][-1],1))
ax2.plot(positief_percentage['x'], positief_percentage['y'], 
         color='gold', linestyle='-', 
         label='Percentage geteste personen positief (nu: ' + huidigpercentage + "%).")

# Plot cases per dag
ax1.plot(positief['x'][:-11], positief['y'][:-11], 
            color='fuchsia', label='Tests positief (totaal '+decimalstring(totaal_positief)+")")
#ax1.plot(positief['x'][-11:], positief['y'][-11:], color='steelblue', linestyle='--', alpha=0.3, label='onvolledig')
ax1.plot(positief_voorspeld['x'][-17:], positief_voorspeld['y'][-17:], 
         color='fuchsia', linestyle=':')

# laat huidige datum zien met vertikale lijn
ax1.axvline(datetime.date.today(), color='teal', linewidth=0.15)

for event in events:
    if 'testsloc' in event:
        anotate(
            ax1, 
            totaaltests['x'],
            totaaltests['y'],
            event['date'], event['event'], 
            event['testsloc'][0], 
            event['testsloc'][1]
        )

ax1.set_xlabel("Datum")
ax1.set_ylabel("Aantal positief")
ax2.set_ylabel("Percentage positief getest")

ax1.set_ylim([0, 40000])
ax2.set_ylim([0, 40])

plt.gca().set_xlim([parser.parse("2020-02-01"), positief_voorspeld['x'][-1]])

gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

plt.title('Positieve COVID-19 tests, '+gegenereerd_op)

footerleft="Gegenereerd op "+gegenereerd_op+".\nSource code: http://github.com/realrolfje/coronadata"
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")


footerright="Publicatiedatum RIVM "+filedate+".\nBron: https://data.rivm.nl/covid-19"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

ax1.legend(loc="upper left")
ax2.legend(loc="upper right")
plt.savefig("../docs/graphs/covidtests.svg", format="svg")
