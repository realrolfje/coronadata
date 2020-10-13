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
events = brondata.readjson('../data/measures-events.json')

print("Calculating ziek graph...")

opgenomen = {
    'x': [],
    'y': []
}

opgenomen_voorspeld = {
    'x': [],
    'y': []
}

geschat_ziek = {
    'x'   : [],
    'y'   : [],
    'min' : [],
    'max' : []
}

geschat_ziek_rna = {
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

date_range = brondata.getDateRange(metenisweten)

for d in date_range:
    datum = d.strftime("%Y-%m-%d")

    # --------------------------------- Normale grafieken (exclusief data van vandaag want dat is altijd incompleet)
    if datum in metenisweten and parser.parse(datum).date() <= datetime.date.today():
        ic['x'].append(parser.parse(datum))
        ic['y'].append(metenisweten[datum]['nu_op_ic'])

        opgenomen['x'].append(parser.parse(datum))
        opgenomen['y'].append(metenisweten[datum]['nu_opgenomen'])

        totaal_positief = metenisweten[datum]['totaal_positief']

        if metenisweten[datum]['rivm-datum']:
            filedate = metenisweten[datum]['rivm-datum']

        if len(ic['y'])>1:
            ic['rc'].append(ic['y'][-1] - ic['y'][-2])
        else:
            ic['rc'].append(0)

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

    # ----------------------- Geschat op basis van RNA
    if datum in metenisweten and metenisweten[datum]['RNA']['besmettelijk']:
        geschat_ziek_rna['x'].append(parser.parse(datum))
        geschat_ziek_rna['y'].append(metenisweten[datum]['RNA']['besmettelijk'])

        geschat_ziek_rna['min'].append(metenisweten[datum]['RNA']['besmettelijk'] * (1-metenisweten[datum]['RNA']['besmettelijk_error']))
        geschat_ziek_rna['max'].append(metenisweten[datum]['RNA']['besmettelijk'] * (1+metenisweten[datum]['RNA']['besmettelijk_error']))
        geschat_ziek_rna_nu = metenisweten[datum]['RNA']['besmettelijk']
    elif datum in metenisweten and metenisweten[datum]['rivm_schatting_besmettelijk']['value']:
        geschat_ziek_rna['x'].append(parser.parse(datum))
        geschat_ziek_rna['y'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['value'])
        geschat_ziek_rna['min'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['min'])
        geschat_ziek_rna['max'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['max'])
    elif len(geschat_ziek_rna['y']) > deltadagen:
        vorig_datum = parser.parse(datum) - datetime.timedelta(days=deltadagen)
        vorig_y = geschat_ziek_rna['y'][-deltadagen]
        nieuw_y = geschat_ziek_rna['y'][-1] + (geschat_ziek_rna['y'][-1] - vorig_y)/deltadagen
        geschat_ziek_rna['x'].append(parser.parse(datum))
        geschat_ziek_rna['y'].append(nieuw_y)

    # Opgenomen voorspeld
    if datum not in metenisweten and len(opgenomen['y']) > deltadagen:
        vorig_datum = parser.parse(datum) - datetime.timedelta(days=deltadagen)
        vorig_y = opgenomen['y'][-deltadagen]
        
        if 'laatste_y' not in locals():
            laatste_y = opgenomen['y'][-1]
        else:
            laatste_y = opgenomen_voorspeld['y'][-1]

        nieuw_y = laatste_y + (laatste_y - vorig_y)/deltadagen

        opgenomen_voorspeld['x'].append(parser.parse(datum))
        opgenomen_voorspeld['y'].append(nieuw_y)

def decimalstring(number):
    return "{:,}".format(number).replace(',','.')


def anotate(plt, metenisweten, datum, tekst, x, y):
    if datum in metenisweten:
        
        # Annotate on RIVM estimates
        # if metenisweten[datum]['rivm_schatting_besmettelijk']['value']:
        #     yval = metenisweten[datum]['rivm_schatting_besmettelijk']['value']
        # else:
        #     indexfromend = len(list(metenisweten.keys())) - list(metenisweten.keys()).index(datum) +7
        #     yval = geschat_ziek['y'][-indexfromend]

        # Annotate on RNA estimates
        if metenisweten[datum]['RNA']['besmettelijk']:
            yval = metenisweten[datum]['RNA']['besmettelijk']
        elif metenisweten[datum]['rivm_schatting_besmettelijk']['value']:
            yval = metenisweten[datum]['rivm_schatting_besmettelijk']['value']
        else:
            yval = None
            # indexfromend = len(list(metenisweten.keys())) - list(metenisweten.keys()).index(datum) +7
            # yval = geschat_ziek_rna['y'][-indexfromend]

        if yval:
            plt.annotate(
                tekst,
                xy=(parser.parse(datum), yval),
                xytext=(parser.parse(x), y),
                fontsize=8,
                bbox=dict(boxstyle='round,pad=0.4', fc='ivory', alpha=1),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.1')
            )

print('Generating daily positive tests graph...')

fig, ax1 = plt.subplots(figsize=(10, 5))
fig.subplots_adjust(top=0.92, bottom=0.13, left=0.09, right=0.91)

ax2 = plt.twinx()

for event in events:
    if 'ziekloc' in event:
        anotate(
            ax2, metenisweten, 
            event['date'], event['event'], 
            event['ziekloc'][0], 
            event['ziekloc'][1]
        )

#plt.figure(figsize =(10,5))
ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)
ax2.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)


nu_opgenomen = opgenomen['y'][-1]
ax1.plot(opgenomen['x'], opgenomen['y'], color='orange', label='aantal opgenomen (nu: '+decimalstring(nu_opgenomen)+')')
ax1.plot(opgenomen_voorspeld['x'], opgenomen_voorspeld['y'], color='orange', linestyle=':')


nu_op_ic = ic['y'][-1]
ax1.plot(ic['x'], ic['y'], color='red', label='aantal op IC (nu: '+decimalstring(nu_op_ic)+')')
ax1.plot(ic_voorspeld['x'], ic_voorspeld['y'], color='red', linestyle=':')

# ax1.plot(opgenomen['x'], opgenomen['y'], color='green',
#          linestyle='-', label='opgenomen (totaal: '+decimalstring(totaal_opgenomen)+')')

# ax2.plot(ziek['x'], ziek['y'], color='darkorange',
#          linestyle=':', label='geschat besmettelijk (nu: '+decimalstring(geschat_besmettelijk)+')')

# Plot ziek based on RIVM
# ax2.plot(geschat_ziek['x'], geschat_ziek['y'], color='steelblue',
#          linestyle=':', 
#          label='RIVM schatting totaal ziek (nu: '+decimalstring(round(geschat_ziek_nu))+')\n'
#                  +'→ 1 op '+str(round(17500000/geschat_ziek_nu))+' mensen is ziek/besmettelijk')
# ax2.fill_between(geschat_ziek['x'][:len(geschat_ziek['min'])], geschat_ziek['min'], geschat_ziek['max'],facecolor='steelblue', alpha=0.1, interpolate=True)

# Plot ziek based on RNA
ax2.plot(geschat_ziek_rna['x'], geschat_ziek_rna['y'], color='steelblue',
         linestyle=':', 
         label='Schatting totaal ziek obv riooldata (nu: '+decimalstring(round(geschat_ziek_rna_nu))+')\n'
                 +'→ 1 op '+str(round(17500000/geschat_ziek_rna_nu))+' mensen is ziek/besmettelijk')
ax2.fill_between(
    geschat_ziek_rna['x'][:len(geschat_ziek_rna['min'])], 
    geschat_ziek_rna['min'], geschat_ziek_rna['max'],
    facecolor='steelblue', alpha=0.1, interpolate=True)


# laat huidige datum zien met vertikale lijn
ax1.axvline(datetime.date.today(), color='teal', linewidth=0.15)

# Horizontale lijn om te checken waar we de IC opnames mee kunnen vergelijken
ax1.axhline(ic['y'][-1], color='red', linestyle=(0, (5, 30)), linewidth=0.2)

ax1.set_xlabel("Datum")
ax1.set_ylabel("Aantal in ziekenhuis / op IC")
ax2.set_ylabel("Geschat ziek")

ax1.set_ylim([0, 3250])
ax2.set_ylim([0, 325000])

plt.gca().set_xlim([parser.parse("2020-02-01"), ic_voorspeld['x'][-1]])

plt.figtext(0.38,0.7, 
         "\"Misschien ben jij klaar met het virus,\n   maar het virus is niet klaar met jou.\"\n    - Hugo de Jonge", 
         color="gray",
         bbox=dict(facecolor='white', alpha=1.0, 
         edgecolor='white'),
         zorder=10)

# ax1.set_yscale('log')
# ax2.set_yscale('log')

gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

plt.title('COVID-19 gerelateerd zieken, '+gegenereerd_op)

footerleft="Gegenereerd op "+gegenereerd_op+".\nSource code: http://github.com/realrolfje/coronadata"
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")


footerright="Publicatiedatum RIVM "+filedate+".\nBronnen: https://data.rivm.nl/covid-19, https://www.stichting-nice.nl/covid-19/"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

ax1.legend(loc="upper left")
ax2.legend(loc="upper right")

plt.savefig("../docs/graphs/zieken.svg", format="svg")
