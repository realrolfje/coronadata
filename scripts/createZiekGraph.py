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

brondata.freshdata()
metenisweten = brondata.readjson('../cache/daily-stats.json')
events = brondata.readjson('../data/measures-events.json')

print("Calculating ziek graph...")

opgenomen = {
    'x': [],
    'y': [],
    'rc': []
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

    # ------------ Totaal positief en laatste meetdatum
    if datum in metenisweten and parser.parse(datum).date() <= datetime.date.today():
        totaal_positief = metenisweten[datum]['totaal_positief']

        if metenisweten[datum]['rivm-datum']:
            filedate = metenisweten[datum]['rivm-datum']


    # --------------- Opname en IC data van vandaag en gisteren zijn niet compleet, niet tonen
    if datum in metenisweten and parser.parse(datum).date() <= (datetime.date.today() - datetime.timedelta(days=3)):
        ic['x'].append(parser.parse(datum))
        ic['y'].append(metenisweten[datum]['nu_op_ic'])

        opgenomen['x'].append(parser.parse(datum))
        opgenomen['y'].append(metenisweten[datum]['nu_opgenomen'])

        if len(ic['y'])>1:
            ic['rc'].append(ic['y'][-1] - ic['y'][-2])
        else:
            ic['rc'].append(0)

        if len(opgenomen['y'])>1:
            opgenomen['rc'].append(opgenomen['y'][-1] - opgenomen['y'][-2])
        else:
            opgenomen['rc'].append(0)


    # ---------------------- Voorspelling op IC obv gemiddelde richtingscoefficient
    if len(ic['x']) > 10 and parser.parse(datum) > ic['x'][-1]:
        ic_rc = mean(ic['rc'][-5:])

        ic_voorspeld['x'].append(parser.parse(datum))
        ic_voorspeld['y'].append(ic['y'][-1] + ic_rc * (parser.parse(datum) - ic['x'][-1]).days )


    # ---------------- Voorspelling opgenomen obv gemiddelde richtingscoefficient
    if len(opgenomen['x']) > 10 and parser.parse(datum) > opgenomen['x'][-1]:
        opgenomen_rc = mean(opgenomen['rc'][-5:])

        opgenomen_voorspeld['x'].append(parser.parse(datum))
        opgenomen_voorspeld['y'].append(opgenomen['y'][-1] + opgenomen_rc * (parser.parse(datum) - opgenomen['x'][-1]).days )

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
    elif datum in metenisweten and metenisweten[datum]['rivm_schatting_besmettelijk']['value'] and parser.parse(datum).date() <= (datetime.date.today() - datetime.timedelta(days=deltadagen)):
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


def anotate(plt, xdata, ydata, datum, tekst, x, y):
    xindex = xdata.index(parser.parse(datum))
    if xindex:
        xval = xdata[xindex]
        yval = ydata[xindex]
        plt.annotate(
            tekst,
            xy=(xval, yval),
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
            ax2, 
            geschat_ziek_rna['x'], geschat_ziek_rna['y'],
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
plt.figtext(0.885,0.125, 
         datetime.datetime.now().strftime("%d"), 
         color="red",
         fontsize=8,
         bbox=dict(facecolor='white', alpha=0.9, pad=0,
         edgecolor='white'),
         zorder=10)
ax1.axvline(datetime.date.today(), color='red', linewidth=0.5)

# Horizontale lijn om te checken waar we de IC opnames mee kunnen vergelijken
ax1.axhline(ic['y'][-1], color='red', linestyle=(0, (5, 30)), linewidth=0.2)

ax1.set_xlabel("Datum")
ax1.set_ylabel("Aantal in ziekenhuis / op IC")
ax2.set_ylabel("Geschat ziek")

ax1.set_ylim([0, 5000])
ax2.set_ylim([0, 500000])

ax2.set_yticks      ([100000,  200000,  300000, 400000, 500000])
ax2.set_yticklabels([ '100k',  '200k', '300k', '400k', '☠'])

plt.gca().set_xlim([parser.parse("2020-03-01"), date_range[-1]])

plt.figtext(0.22,0.7, 
         "\"Misschien ben jij klaar met het virus,\n   maar het virus is niet klaar met jou.\"\n    - Hugo de Jonge", 
         color="gray",
         bbox=dict(facecolor='white', alpha=1.0, 
         edgecolor='white'),
         zorder=10)


gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
data_tot=opgenomen['x'][-1].strftime("%Y-%m-%d")

plt.title('COVID-19 gerelateerd zieken')

footerleft="Gegenereerd op "+gegenereerd_op+", o.b.v. data tot "+data_tot+".\nSource code: http://github.com/realrolfje/coronadata"
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")


footerright="Publicatiedatum RIVM "+filedate+".\nBronnen: https://data.rivm.nl/covid-19, https://www.stichting-nice.nl/covid-19/"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

ax1.legend(loc="upper left")
ax2.legend(loc="upper right")

plt.savefig("../docs/graphs/zieken.svg", format="svg")
