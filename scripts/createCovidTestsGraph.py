#!/usr/bin/env python3
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
from dateutil import parser
from statistics import mean
import datetime
import json
import modules.brondata as brondata


brondata.freshdata()
metenisweten = brondata.readjson('../cache/daily-stats.json')

print("Calculating predictions...")

positief = {
    'x': [],
    'y': []
}

totaaltests = {
    'x': [],
    'y': []
}

positief_percentage = {
    'x': [],
    'y': []
}


opgenomen = {
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

geschat_ziek = {
    'x'   : [],
    'y'   : [],
    'min' : [],
    'max' : []
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

date_range = brondata.getDateRange(metenisweten)

for d in date_range:
    datum = d.strftime("%Y-%m-%d")

    # --------------------------------- Normale grafieken (exclusief data van vandaag want dat is altijd incompleet)
    if datum in metenisweten and parser.parse(datum).date() <= datetime.date.today():
        positief['x'].append(parser.parse(datum))
        positief['y'].append(metenisweten[datum]['positief'])

        ic['x'].append(parser.parse(datum))
        ic['y'].append(metenisweten[datum]['nu_op_ic'])

        opgenomen['x'].append(parser.parse(datum))
        opgenomen['y'].append(metenisweten[datum]['opgenomen'])

        if metenisweten[datum]['rivm_totaal_tests']:
            totaaltests['x'].append(parser.parse(datum))
            totaaltests['y'].append(metenisweten[datum]['rivm_totaal_tests'])

        if metenisweten[datum]['rivm_totaal_tests'] and metenisweten[datum]['positief']:
            positief_percentage['x'].append(parser.parse(datum))
            positief_percentage['y'].append(100 * metenisweten[datum]['positief'] / metenisweten[datum]['rivm_totaal_tests'])

        totaal_positief = metenisweten[datum]['totaal_positief']

        if metenisweten[datum]['rivm-datum']:
            filedate = metenisweten[datum]['rivm-datum']

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


    # ---------------------- Voorspelling op IC obv gemiddelde richtingscoefficient positief getest.
    if len(ic['x']) > 10 and parser.parse(datum) > ic['x'][-1]:
        ic_rc = mean(ic['rc'][-5:])

        ic_voorspeld['x'].append(parser.parse(datum))
        ic_voorspeld['y'].append(ic['y'][-1] + ic_rc * (parser.parse(datum) - ic['x'][-1]).days )

    # ----------------------- Trek "geschat ziek" op basis van RC nog even door.
    deltadagen = 15
    if datum in metenisweten and metenisweten[datum]['rivm_schatting_besmettelijk']['value']:
        geschat_ziek['x'].append(parser.parse(datum))
        geschat_ziek['y'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['value'])
        geschat_ziek['min'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['min'])
        geschat_ziek['max'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['max'])
        geschat_ziek_nu = metenisweten[datum]['rivm_schatting_besmettelijk']['value']
    elif len(geschat_ziek['y']) > deltadagen:
        vorig_datum = parser.parse(datum) - datetime.timedelta(days=deltadagen)
        vorig_y = geschat_ziek['y'][-deltadagen]
        nieuw_y = geschat_ziek['y'][-1] + (geschat_ziek['y'][-1] - vorig_y)/deltadagen
        geschat_ziek['x'].append(parser.parse(datum))
        geschat_ziek['y'].append(nieuw_y)


def decimalstring(number):
    return "{:,}".format(number).replace(',','.')


def anotate(plt, metenisweten, datum, tekst, x, y):
    if datum in metenisweten:
        plt.annotate(
            tekst,
            xy=(parser.parse(datum), metenisweten[datum]['positief']),
            xytext=(parser.parse(x), y),
            fontsize=8,
            bbox=dict(boxstyle='round,pad=0.4', fc='ivory', alpha=1),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.1')
        )

print('Generating daily positive tests graph...')

fig, ax1 = plt.subplots(figsize=(10, 5))
fig.subplots_adjust(bottom=0.2, left=0.09, right=0.91)

ax2 = plt.twinx()

ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)
ax2.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)

# Plot cases per dag
ax1.plot(positief['x'][:-10], positief['y'][:-10], color='steelblue', label='positief getest (totaal '+decimalstring(totaal_positief)+")")
ax1.plot(positief['x'][-11:], positief['y'][-11:], color='steelblue', linestyle='--', alpha=0.3, label='onvolledig')

ax1.text(parser.parse("2020-05-01"), 20000, "Geen smoesjes, je weet het best.\nAls je niet ziek wordt, hoef je ook niet getest.", color="gray")

ax1.plot(positief_voorspeld['x'][-17:], positief_voorspeld['y'][-17:], 
         color='steelblue', linestyle=':', label='voorspeld')

ax1.plot(totaaltests['x'], totaaltests['y'], 
         color='lightgreen', linestyle='-', label='Totaal afgenomen tests')

huidigpercentage = decimalstring(round(positief_percentage['y'][-1],1))
ax2.plot(positief_percentage['x'], positief_percentage['y'], 
         color='red', linestyle='-', label='Percentage positieve tests (nu: ' + huidigpercentage + "%).")
         

# laat huidige datum zien met vertikale lijn
ax1.axvline(positief['x'][-1], color='teal', linewidth=0.15)

ax1.set_xlabel("Datum")
ax1.set_ylabel("Aantal positief")
ax2.set_ylabel("Percentage positief getest")

ax1.set_ylim([0, 40000])
ax2.set_ylim([0, 40])

plt.gca().set_xlim([parser.parse("2020-02-01"), ic_voorspeld['x'][-1]])

gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

plt.title('Positieve COVID-19 tests, '+gegenereerd_op)

footerleft="Gegenereerd op "+gegenereerd_op+".\nSource code: http://github.com/realrolfje/coronadata"
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")


footerright="Publicatiedatum RIVM "+filedate+".\nBron: https://data.rivm.nl/covid-19"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

ax1.legend(loc="upper left")
ax2.legend(loc="upper right")
plt.savefig("../graphs/covidtests.png", format="png")
plt.savefig("../graphs/covidtests.svg", format="svg")
