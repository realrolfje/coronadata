#!/usr/bin/env python3
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
from dateutil import parser
from statistics import mean
import datetime
import modules.brondata as brondata
from modules.brondata import decimalstring
from modules.datautil import anotate
import sys
from modules.datautil import runIfNewData
from modules.datecache import dateCache


def main():
    runIfNewData(__file__)
    metenisweten = brondata.readjson('../data/daily-stats.json')
    createZiekenhuisTotaalGraph(metenisweten)

def createZiekenhuisTotaalGraph(metenisweten):
    print("Calculating 'totaal in ziekenhuis' graph...")

    opgenomen = {
        'x': [],
        'y': [],
        'rc': []
    }

    ic = {
        'x' : [],
        'y' : [],
        'rc' : []
    }

    totaal = []

    date_range = brondata.getDateRange(metenisweten)

    for d in date_range:
        datum = d.strftime("%Y-%m-%d") # Convert back to String
        m = metenisweten.get(datum)

        # ------------ Totaal positief en laatste meetdatum
        if m and dateCache.isvaliddate(datum):
            if m['rivm-datum']:
                filedate = m['rivm-datum']


        # --------------- Opname en IC data van vandaag en gisteren zijn niet compleet, niet tonen
        if m and dateCache.parse(datum).date() <= (datetime.date.today() - datetime.timedelta(days=3)):
            nu_op_ic = m.get('nu_op_ic') or None
            nu_opgenomen = m.get('nu_opgenomen') or None

            if nu_op_ic != None and nu_opgenomen != None:
                ic['x'].append(dateCache.parse(datum))
                ic['y'].append(nu_op_ic)

                opgenomen['x'].append(dateCache.parse(datum))
                opgenomen['y'].append(nu_opgenomen)
            
                totaal.append(ic['y'][-1] + opgenomen['y'][-1])
        else:
            print(f"skipped {datum}")

    print('Generating total hospitalized graph')

    fig, ax1 = plt.subplots(figsize=(10, 5))
    fig.subplots_adjust(top=0.92, bottom=0.13, left=0.09, right=0.91)

    ax1.grid(which='both', axis='both', linestyle='-.',
            color='gray', linewidth=1, alpha=0.3)

    nu_opgenomen = opgenomen['y'][-1]
    nu_op_ic = ic['y'][-1]
    nu_totaal = totaal[-1]

    plt.stackplot(
        opgenomen['x'],
        ic['y'],
        opgenomen['y'],
        colors=['red', 'orange'],
        labels=[
            'aantal op IC (nu: '+decimalstring(nu_op_ic)+')',
            'aantal op verpleegafdeling (nu: '+decimalstring(nu_opgenomen)+')'
        ]
    )

    plt.plot(
        opgenomen['x'],
        totaal,
        color='black',
        label='Totaal (%s)' % decimalstring(nu_totaal)
    )

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

    ax1.set_ylim([0, 5000])

    plt.gca().set_xlim([parser.parse("2020-03-01"), date_range[-1]])


    gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    data_tot=opgenomen['x'][-1].strftime("%Y-%m-%d")

    plt.title('COVID-19 patienten in het ziekenhuis')

    footerleft="Gegenereerd op "+gegenereerd_op+", o.b.v. data tot "+data_tot+".\nSource code: http://github.com/realrolfje/coronadata"
    plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")


    footerright="Publicatiedatum RIVM "+filedate+".\nBronnen: https://data.rivm.nl/covid-19, https://www.stichting-nice.nl/covid-19/"
    plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

    ax1.legend(loc="upper left")

    plt.savefig("../docs/graphs/totaal-mensen-in-ziekenhuis.svg", format="svg")

if __name__ == '__main__':
    sys.exit(main())