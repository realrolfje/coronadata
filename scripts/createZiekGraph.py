#!/usr/bin/env python3
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
from dateutil import parser
from statistics import mean
import datetime
import modules.arguments as arguments
import modules.brondata as brondata
from modules.brondata import decimalstring, dateCache
from modules.datautil import runIfNewData, anotate
import sys

def main():
    runIfNewData(__file__)
    metenisweten = brondata.readjson('../data/daily-stats.json')
    events = brondata.readjson('../data/measures-events.json')
    createZiekGraph(metenisweten, events)

def createZiekGraph(metenisweten, events):
    graphname="zieken"

    print("Calculating "+graphname+" graph...")

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

    lastDays = arguments.lastDays()
    if (lastDays>0):
        date_range = date_range[-lastDays:]

    filedate = 'onbekend'

    for d in date_range:
        datum = d.strftime("%Y-%m-%d")

        # ------------ Totaal positief en laatste meetdatum
        if datum in metenisweten and dateCache.parse(datum).date() <= dateCache.today():
            totaal_positief = metenisweten[datum]['totaal_positief']

            if metenisweten[datum]['rivm-datum']:
                filedate = metenisweten[datum]['rivm-datum']


        # --------------- Opname en IC data van vandaag en gisteren zijn niet compleet, niet tonen
        if datum in metenisweten and dateCache.parse(datum).date() <= (dateCache.today() - datetime.timedelta(days=3)):
            if 'nu_op_ic' in metenisweten[datum] and metenisweten[datum]['nu_op_ic']:
                ic['x'].append(dateCache.parse(datum))
                ic['y'].append(metenisweten[datum]['nu_op_ic'])

                if len(ic['y'])>1:
                    ic['rc'].append(ic['y'][-1] - ic['y'][-2])
                else:
                    ic['rc'].append(0)

            if 'nu_opgenomen' in metenisweten[datum] and metenisweten[datum]['nu_opgenomen']:
                opgenomen['x'].append(dateCache.parse(datum))
                opgenomen['y'].append(metenisweten[datum]['nu_opgenomen'])

                if len(opgenomen['y'])>1:
                    opgenomen['rc'].append(opgenomen['y'][-1] - opgenomen['y'][-2])
                else:
                    opgenomen['rc'].append(0)


        # ---------------------- Voorspelling op IC obv gemiddelde richtingscoefficient
        if len(ic['x']) > 10 and dateCache.parse(datum) > ic['x'][-1]:
            ic_rc = mean(ic['rc'][-5:])

            ic_voorspeld['x'].append(dateCache.parse(datum))
            ic_voorspeld['y'].append(ic['y'][-1] + ic_rc * (dateCache.parse(datum) - ic['x'][-1]).days )


        # ---------------- Voorspelling opgenomen obv gemiddelde richtingscoefficient
        if len(opgenomen['x']) > 10 and dateCache.parse(datum) > opgenomen['x'][-1]:
            opgenomen_rc = mean(opgenomen['rc'][-5:])

            opgenomen_voorspeld['x'].append(dateCache.parse(datum))
            opgenomen_voorspeld['y'].append(opgenomen['y'][-1] + opgenomen_rc * (dateCache.parse(datum) - opgenomen['x'][-1]).days )

        # ----------------------- Trek "geschat ziek" op basis van RC nog even door.
        deltadagen = 15
        if datum in metenisweten and metenisweten[datum]['rivm_schatting_besmettelijk']['value']:
            geschat_ziek['x'].append(dateCache.parse(datum))
            geschat_ziek['y'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['value'])
            geschat_ziek['min'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['min'])
            geschat_ziek['max'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['max'])
            geschat_ziek_nu = metenisweten[datum]['rivm_schatting_besmettelijk']['value']
        elif len(geschat_ziek['y']) > deltadagen:
            vorig_datum = dateCache.parse(datum) - datetime.timedelta(days=deltadagen)
            vorig_y = geschat_ziek['y'][-deltadagen]
            nieuw_y = geschat_ziek['y'][-1] + (geschat_ziek['y'][-1] - vorig_y)/deltadagen
            geschat_ziek['x'].append(dateCache.parse(datum))
            geschat_ziek['y'].append(nieuw_y)

        # ----------------------- Geschat op basis van RNA
        # if datum in metenisweten and metenisweten[datum]['RNA']['besmettelijk']:
        #     geschat_ziek_rna['x'].append(dateCache.parse(datum))
        #     geschat_ziek_rna['y'].append(metenisweten[datum]['RNA']['besmettelijk'])
        #     geschat_ziek_rna['min'].append(metenisweten[datum]['RNA']['besmettelijk'] * (1-metenisweten[datum]['RNA']['besmettelijk_error']))
        #     geschat_ziek_rna['max'].append(metenisweten[datum]['RNA']['besmettelijk'] * (1+metenisweten[datum]['RNA']['besmettelijk_error']))
        #     geschat_ziek_rna_nu = metenisweten[datum]['RNA']['besmettelijk']
        # elif datum in metenisweten and metenisweten[datum]['rivm_schatting_besmettelijk']['value'] and dateCache.parse(datum) <= (dateCache.today() - datetime.timedelta(days=deltadagen)):
        #     geschat_ziek_rna['x'].append(dateCache.parse(datum))
        #     geschat_ziek_rna['y'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['value'])
        #     geschat_ziek_rna['min'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['min'])
        #     geschat_ziek_rna['max'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['max'])
        # elif len(geschat_ziek_rna['y']) > deltadagen:
        #     vorig_datum = dateCache.parse(datum) - datetime.timedelta(days=deltadagen)
        #     vorig_y = geschat_ziek_rna['y'][-deltadagen]
        #     nieuw_y = geschat_ziek_rna['y'][-1] + (geschat_ziek_rna['y'][-1] - vorig_y)/deltadagen
        #     geschat_ziek_rna['x'].append(dateCache.parse(datum))
        #     geschat_ziek_rna['y'].append(nieuw_y)

        # ----------------------- Geschat op basis van eigen berekening
        if datum in metenisweten and metenisweten[datum]['rolf_besmettelijk']:
            geschat_ziek_rna['x'].append(dateCache.parse(datum))
            geschat_ziek_rna['y'].append(metenisweten[datum]['rolf_besmettelijk'])
            geschat_ziek_rna['min'].append(metenisweten[datum]['rolf_besmettelijk'] * 0.7)
            geschat_ziek_rna['max'].append(metenisweten[datum]['rolf_besmettelijk'] * 1.3)
            geschat_ziek_rna_nu = geschat_ziek_rna['y'][-1]
        elif datum in metenisweten and metenisweten[datum]['rivm_schatting_besmettelijk']['value'] and dateCache.parse(datum).date() <= (dateCache.today() - datetime.timedelta(days=deltadagen)):
            geschat_ziek_rna['x'].append(dateCache.parse(datum))
            geschat_ziek_rna['y'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['value'])
            geschat_ziek_rna['min'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['min'])
            geschat_ziek_rna['max'].append(metenisweten[datum]['rivm_schatting_besmettelijk']['max'])
        elif len(geschat_ziek_rna['y']) > deltadagen:
            vorig_datum = dateCache.parse(datum) - datetime.timedelta(days=deltadagen)
            vorig_y = geschat_ziek_rna['y'][-deltadagen]
            nieuw_y = geschat_ziek_rna['y'][-1] + (geschat_ziek_rna['y'][-1] - vorig_y)/deltadagen
            geschat_ziek_rna['x'].append(dateCache.parse(datum))
            geschat_ziek_rna['y'].append(nieuw_y)


    print('Generating daily positive tests graph...')

    fig, ax1 = plt.subplots(figsize=(10, 5))
    fig.subplots_adjust(top=0.92, bottom=0.13, left=0.09, right=0.91)

    ax2 = plt.twinx()

    for event in events:
        if graphname in event \
            and dateCache.parse(event[graphname][0]) > date_range[0]\
            and (len(event[graphname]) <= 2 or len(date_range) <= event[graphname][2]):
            anotate(
                ax2, 
                geschat_ziek_rna['x'], geschat_ziek_rna['y'],
                event['date'], event['event'], 
                event[graphname][0], 
                event[graphname][1]
            )

    #plt.figure(figsize =(10,5))
    ax1.grid(which='both', axis='both', linestyle='-.',
            color='gray', linewidth=1, alpha=0.3)
    ax2.grid(which='both', axis='both', linestyle='-.',
            color='gray', linewidth=1, alpha=0.3)


    nu_opgenomen = opgenomen['y'][-1]
    ax1.plot(opgenomen['x'], opgenomen['y'], color='orange', label='aantal op verpleegafdeling (nu: '+decimalstring(nu_opgenomen)+')')
    ax1.plot(opgenomen_voorspeld['x'], opgenomen_voorspeld['y'], color='orange', linestyle=':')


    nu_op_ic = ic['y'][-1]
    ax1.plot(ic['x'], ic['y'], color='red', label='aantal op IC (nu: '+decimalstring(nu_op_ic)+')')
    ax1.plot(ic_voorspeld['x'], ic_voorspeld['y'], color='red', linestyle=':')

    # Plot ziek based on RNA
    ax2.plot(geschat_ziek_rna['x'], geschat_ziek_rna['y'], color='steelblue',
            linestyle=':', 
            label='Schatting totaal ziek (nu: '+decimalstring(round(geschat_ziek_rna_nu))+')\n'
                    +'→ 1 op '+str(round(17500000/geschat_ziek_rna_nu))+' mensen is ziek/besmettelijk')
    ax2.fill_between(
        geschat_ziek_rna['x'][:len(geschat_ziek_rna['min'])], 
        geschat_ziek_rna['min'], geschat_ziek_rna['max'],
        facecolor='steelblue', alpha=0.1, interpolate=True)

    # Put vertical line at current day
    plt.text(
        x=dateCache.today(),
        y=0,
        s=datetime.datetime.now().strftime("%d"), 
        color="white",
        fontsize=8,
        ha="center",
        va="center",
        bbox=dict(boxstyle='round,pad=0.1', facecolor='red', alpha=1, edgecolor='red'),
        zorder=10
    )
    plt.axvline(dateCache.today(), color='red', linewidth=0.5)

    # Horizontale lijn om te checken waar we de IC opnames mee kunnen vergelijken
    ax1.axhline(ic['y'][-1], color='red', linestyle=(0, (5, 30)), linewidth=0.2)

    ax1.set_xlabel("Datum")
    ax1.set_ylabel("Aantal op verpleegafdeling / op IC")
    ax2.set_ylabel("Geschat ziek")

    ax1.set_ylim([0, 3000])
    ax2.set_ylim([0, 1200000])

    ax2.set_yticks      ([200000, 400000, 600000, 800000, 1000000, 1200000])
    ax2.set_yticklabels([ '200k', '400k', '600k', '800k', '1000k',     '☠'])

    plt.gca().set_xlim([date_range[0], date_range[-1]])

    gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    data_tot=opgenomen['x'][-1].strftime("%Y-%m-%d")

    plt.title('COVID-19 gerelateerd zieken')

    footerleft="Gegenereerd op "+gegenereerd_op+", o.b.v. data tot "+data_tot+".\nSource code: http://github.com/realrolfje/coronadata"
    plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")

    footerright="Publicatiedatum RIVM "+filedate+".\nBronnen: https://data.rivm.nl/covid-19, https://www.stichting-nice.nl/covid-19/"
    plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")

    if (lastDays > 0):
        plt.savefig("../docs/graphs/"+graphname+"-"+str(lastDays)+".svg", format="svg")
    else:
        plt.savefig("../docs/graphs/"+graphname+".svg", format="svg")

    dateCache.cacheReport()

if __name__ == '__main__':
    sys.exit(main())