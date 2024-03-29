#!/usr/bin/env python3
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
from dateutil import parser
import datetime
import sys
import modules.brondata as brondata
import modules.arguments as arguments
from modules.brondata import decimalstring, dateCache
from modules.datautil import anotate
from modules.datautil import runIfNewData


def main():
    runIfNewData(__file__)
    metenisweten = brondata.readjson('../data/daily-stats.json')
    events = brondata.readjson('../data/measures-events.json')
    createCovidTestsGraph(metenisweten, events)

def createCovidTestsGraph(metenisweten, events):
    print("Calculating predictions...")

    # personen_positief = {
    #     'x': [],
    #     'y': []
    # }

    positief = {
        'x': [],
        'y': []
    }

    positief_voorspeld = {
        'x': [],
        'y': [],
        'avgsize':7
    }

    totaaltests = {
        'x': [],
        'y': [],
        'total': 0
    }

    positief_percentage = {
        'x': [],
        'y': []
    }

    date_range = brondata.getDateRange(metenisweten)

    lastDays = arguments.lastDays()
    if (lastDays>0):
        date_range = date_range[-lastDays:]


    for d in date_range:
        datum = d.strftime("%Y-%m-%d")

        # --------------------------------- Normale grafieken (exclusief data van vandaag want dat is altijd incompleet)
        if datum in metenisweten and dateCache.parse(datum).date() <= (dateCache.today()):
            # positief['x'].append(dateCache.parse(datum))
            # positief['y'].append(metenisweten[datum]['positief'])

            if 'rivm_totaal_tests' in metenisweten[datum] and metenisweten[datum]['rivm_totaal_tests']:
                totaaltests['x'].append(dateCache.parse(datum))
                totaaltests['y'].append(metenisweten[datum]['rivm_totaal_tests'])
                totaaltests['total'] += int(metenisweten[datum]['rivm_totaal_tests'])
            elif 'rivm_totaal_personen_getest' in metenisweten[datum] and metenisweten[datum]['rivm_totaal_personen_getest']:
                totaaltests['x'].append(dateCache.parse(datum))
                totaaltests['y'].append(metenisweten[datum]['rivm_totaal_personen_getest'])
                totaaltests['total'] += int(metenisweten[datum]['rivm_totaal_personen_getest'])
            # else:
            #     print("no totaal for "+datum)

            if 'rivm_totaal_tests_positief' in metenisweten[datum] and metenisweten[datum]['rivm_totaal_tests_positief']:
                positief['x'].append(dateCache.parse(datum))
                positief['y'].append(metenisweten[datum]['rivm_totaal_tests_positief'])

                positief_percentage['x'].append(dateCache.parse(datum))
                positief_percentage['y'].append(100 * positief['y'][-1] / totaaltests['y'][-1])

            elif 'rivm_totaal_personen_positief' in metenisweten[datum] and metenisweten[datum]['rivm_totaal_personen_positief']:
                positief['x'].append(dateCache.parse(datum))
                positief['y'].append(metenisweten[datum]['rivm_totaal_personen_positief'])

                positief_percentage['x'].append(dateCache.parse(datum))
                positief_percentage['y'].append(100 * positief['y'][-1] / totaaltests['y'][-1])
            # else:
            #     print("no tests for "+datum)
        
            if datum in metenisweten:
                totaal_positief = metenisweten[datum]['totaal_positief']

            if metenisweten[datum]['rivm-datum']:
                filedate = metenisweten[datum]['rivm-datum']

        # ---------------------- Voorspelling positief getst obv gemiddelde richtingscoefficient positief getest.
        if datum in metenisweten and len(positief['y']) > positief_voorspeld['avgsize'] \
            and dateCache.parse(datum) < (datetime.datetime.now() - datetime.timedelta(days=positief_voorspeld['avgsize'])):
            # Voorspel morgen op basis van metingen
            rc = (positief['y'][-1]-positief['y'][-positief_voorspeld['avgsize']]) / positief_voorspeld['avgsize']
            positief_voorspeld['x'].append(dateCache.parse(datum) + datetime.timedelta(days=1))
            positief_voorspeld['y'].append(positief['y'][-1] + rc)
        elif len(positief_voorspeld['y']) > positief_voorspeld['avgsize']:
            # Voorspel morgen op basis van schatting gisteren
            rc = (positief_voorspeld['y'][-1]-positief_voorspeld['y'][-positief_voorspeld['avgsize']]) / positief_voorspeld['avgsize']
            positief_voorspeld['x'].append(dateCache.parse(datum) + datetime.timedelta(days=1))
            positief_voorspeld['y'].append(positief_voorspeld['y'][-1] + rc)
        elif len(positief['y']) > 0:
            # If all else fails neem waarde van vorige positief
            positief_voorspeld['x'].append(dateCache.parse(datum) + datetime.timedelta(days=1))
            positief_voorspeld['y'].append(positief['y'][-1])
        # else:
        #     print('no data to calculate RC')


    print('Generating daily positive tests graph...')

    fig, ax1 = plt.subplots(figsize=(10, 5))
    fig.subplots_adjust(top=0.92, bottom=0.13, left=0.09, right=0.91)

    ax2 = plt.twinx()

    ax1.grid(which='both', axis='both', linestyle='-.',
            color='gray', linewidth=1, alpha=0.3)
    ax2.grid(which='both', axis='both', linestyle='-.',
            color='gray', linewidth=1, alpha=0.3)

    ax1.text(
        dateCache.parse("2020-04-15"), 45500, 
        "Geen smoesjes,\nje weet het best.\nAls je niet ziek wordt,\nhoef je ook niet getest.", 
        color="gray",
        bbox=dict(facecolor='white', alpha=1.0, edgecolor='white'),
        zorder=10)


    ax1.plot(totaaltests['x'], totaaltests['y'], 
            color='lightblue', linestyle='-', label='Uitgevoerde tests (nu: '+decimalstring(totaaltests['y'][-1])+')')

    # Plot cases per dag
    totaal_percentage = round(100*totaal_positief/totaaltests['total'],1)
    ax1.plot(positief['x'][:-positief_voorspeld['avgsize']], 
            positief['y'][:-positief_voorspeld['avgsize']], 
                color='fuchsia', label=
                "Tests positief (nu: %s)"
                % decimalstring(positief['y'][-1])
    )
    #ax1.plot(positief['x'][-11:], positief['y'][-11:], color='steelblue', linestyle='--', alpha=0.3, label='onvolledig')
    ax1.plot(positief_voorspeld['x'][-positief_voorspeld['avgsize']-7:], positief_voorspeld['y'][-positief_voorspeld['avgsize']-7:], 
            color='fuchsia', linestyle=':')

    huidigpercentage = decimalstring(round(positief_percentage['y'][-1],1))
    ax2.plot(positief_percentage['x'], positief_percentage['y'], 
            color='gold', linestyle='-', 
            label='Percentage positieve tests (%s%%).'
            % ( huidigpercentage)
    )

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

    for event in events:
        if 'testsloc' in event and dateCache.parse(event['testsloc'][0]) > date_range[0]:
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

    ax1.set_ylim([0, 160000])
    ax1.set_yticks      ([20000, 40000, 60000, 80000, 100000, 120000, 140000, 160000])
    ax1.set_yticklabels([ '20k', '40k', '60k', '80k', '100k', '120k', '140k', '160k'])

    ax2.set_ylim([0, 80])

    plt.gca().set_xlim([date_range[0], date_range[-1]])

    gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    data_tot=positief['x'][-11].strftime("%Y-%m-%d")

    plt.title('Positieve COVID-19 tests')

    footerleft="Gegenereerd op "+gegenereerd_op+", o.b.v. data tot "+data_tot+".\nSource code: http://github.com/realrolfje/coronadata"
    plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")


    footerright="Publicatiedatum RIVM "+filedate+".\nBron: https://data.rivm.nl/covid-19"
    plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")

    if (lastDays > 0):
        plt.savefig("../docs/graphs/covidtests-"+str(lastDays)+".svg", format="svg")
    else:
        plt.savefig("../docs/graphs/covidtests.svg", format="svg")

    dateCache.cacheReport()

if __name__ == '__main__':
    sys.exit(main())