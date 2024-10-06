#!/usr/bin/env python3
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
from dateutil.relativedelta import relativedelta
import datetime
import json
import modules.arguments as arguments
import modules.brondata as brondata
from modules.brondata import dateCache
from modules.datautil import runIfNewData, anotate
import sys

def main():
    runIfNewData(__file__)
    metenisweten = brondata.readjson('../data/daily-stats.json')
    events = brondata.readjson('../data/measures-events.json')
    createHeatmap(metenisweten, events)

def createHeatmap(metenisweten, events):
    print("Generating date/age heatmap.")

    xlabels = []
    x = []
    y = []

    date_range = brondata.getDateRange(metenisweten)
    lastDays = arguments.lastDays()
    if (lastDays>0):
        date_range = date_range[-lastDays:]

    startdate = date_range[0]

    weightsmap={}

    # The heatmap data is already in metenisweten, we can optimze. Complete this:
    # metenisweten = brondata.readjson('../data/daily-stats.json')
    # print("Converting records to x/y data")
    # for date_statistics in metenisweten:
    #     if date_statistics > startdate:
    #         for age in metenisweten[date_statistics]['besmettingleeftijd']:
    #             datax = (date_statistics - startdate).days
    #             datay = metenisweten[date_statistics]['besmettingleeftijd']

    datelog = []

    with open('../cache/COVID-19_casus_landelijk.json', 'r') as json_file:
        data = json.load(json_file)
        print("Converting records to x/y data")
        for record in data:
            date_statistics = dateCache.parse(record['Date_statistics'])
            if date_statistics >= startdate:
                datelog.append(date_statistics)
                try:
                    datax = (date_statistics - startdate).days
                    datay = int(record['Agegroup'].split('-')[0].split('+')[0])+5
                    filedate = record['Date_file']
                    x.append(datax)
                    y.append(datay)

                    # if datax not in weightsmap:
                    #     weightsmap[datax] = 1
                    # else:
                    #     weightsmap[datax] = weightsmap[datax] + 1

                except ValueError:
                    # print('ERROR '+record['Date_statistics'] + ' | ' + record['Agegroup'])
                    pass

    # print("Calculating weights.")
    # weights=[]
    # for d in x:
    #     weights.append(1./weightsmap[d])

    # Averages
    gemiddeldeleeftijd = {
        'x': [],
        'y': []
    }


    for d in date_range:
        datum = d.strftime("%Y-%m-%d")
        if datum in metenisweten and metenisweten[datum]['besmettingleeftijd_gemiddeld'] is not None:
            gemiddeldeleeftijd['x'].append(d)
            gemiddeldeleeftijd['y'].append(metenisweten[datum]['besmettingleeftijd_gemiddeld'])

    gemiddeldlaatsteweek = int(round(sum(gemiddeldeleeftijd['y'][-7:])/7))

    gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    fig, heatmap = plt.subplots(figsize=(10, 4), constrained_layout=True, sharex='all', sharey='all')
    fig.subplots_adjust(top=0.92, bottom=0.17, left=0.09, right=0.91)
    averages = plt.twinx()

    plt.title('Positieve tests per leeftijdsgroep')

    print("Plotting heatmap, "+str(len(x))+"x"+str(len(y)))

    # Gewogen:
    #plt.hist2d(x, y, bins=[x[-1]+7,10], range=[[0,x[-1]+7],[0,100]], cmap='inferno', weights=weights)

    # Ongewogen:
    try:
        heatmap.hist2d(
            x, y, 
            bins=[120,10], range=[[0,x[-1]+7],[0,100]], 
            cmin=1, cmap='Blues'
        ) # inferno is also a good one
    except IndexError as e:
        print("Error bij maken heatmap: "+e)

    leeftijdx = [(x-startdate).days for x in gemiddeldeleeftijd['x']]
    # print("Heatmap runs from %d to %d" % (min(x), max(x)))
    # print("Heatmap runs from %s to %s" % (datelog[0], datelog[-1]))
    # print("Average runs from %d to %d" % (min(leeftijdx), max(leeftijdx)))
    # print("Average runs from %s to %s" % (gemiddeldeleeftijd['x'][0], gemiddeldeleeftijd['x'][-1]))
    averages.plot(
        leeftijdx, 
        gemiddeldeleeftijd['y'], 
        color='darkred', alpha=0.5, 
        label='Gemiddelde leeftijd (laatste week: '+str(gemiddeldlaatsteweek)+')'
    )

    averages.legend(loc="upper right")

    graphname='heatmap'
    for event in events:
        if graphname in event \
            and dateCache.parse(event[graphname][0]) > date_range[0]\
            and (len(event[graphname]) <= 2 or len(date_range) <= event[graphname][2]):

            eventDateIndex = (dateCache.parse(event['date']) - startdate).days
            textboxIndex =  (dateCache.parse(event[graphname][0]) - startdate).days
            anotate(
                averages, 
                leeftijdx, gemiddeldeleeftijd['y'],
                eventDateIndex, event['event'], 
                textboxIndex, 
                event[graphname][1]
            )

    heatmap.set(
        xlim=[x[0], x[-1]+7],
        xbound=([x[0], x[-1]+7]),
        ylim=[0, 100],
        autoscale_on=False
    )
    averages.set(
        xlim=([x[0], x[-1]+7]),
        xbound=([x[0], x[-1]+7]),
        ylim=[0, 100],
        autoscale_on=False
    )

    # Dirty stuff to get x labels (needs cleanup)
    xlabeldates = [
        (startdate + relativedelta(months=x)) - datetime.timedelta(days = (startdate.day - 1))
        # startdate + relativedelta(months=x)
        for x in range(
            gemiddeldeleeftijd['x'][-1].month - startdate.month + ((gemiddeldeleeftijd['x'][-1].year - startdate.year) * 12) + 1)
    ]

    print(gemiddeldeleeftijd['x'][-1])

    xlabels = []
    xlocs = []
    for label in xlabeldates:
        # print(label)
        if ((label - startdate).days + 1 >= 0) and (len(date_range) <= 365 or (int(label.strftime("%m")) % 2) != 0):
            xlabels.append(label.strftime("%Y-%m"))
            xlocs.append((label - startdate).days + 1)
    locs, labels = plt.xticks(xlocs, xlabels)

    # Labels and tickmarks
    heatmap.set_xlabel("Datum")
    heatmap.set_ylabel("Leeftijd")

    # Put vertical line at current day
    plt.text(
        x=(datetime.date.today() - startdate.date()).days,
        y=0,
        s=datetime.datetime.now().strftime("%d"), 
        color="white",
        fontsize=8,
        ha="center",
        va="center",
        bbox=dict(boxstyle='round,pad=0.1', facecolor='red', alpha=1, edgecolor='red'),
        zorder=10
    )
    averages.axvline((datetime.date.today() - startdate.date()).days, color='red', linewidth=0.5)

    # averages.axvline((datetime.date.today() - startdate.date()).days, color='red', linewidth=0.5)

    data_tot = gemiddeldeleeftijd['x'][-1].strftime("%Y-%m-%d")
    footerleft="Gegenereerd op "+gegenereerd_op+" o.b.v. data tot "+data_tot+".\nSource code: http://github.com/realrolfje/coronadata"
    plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")

    footerright="Publicatiedatum RIVM "+filedate+".\nBron: https://data.rivm.nl/covid-19"
    plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

    heatmap.grid(which='both', axis='both', linestyle='-.',
                color='gray', linewidth=1, alpha=0.3)

    if (lastDays > 0):
        plt.savefig("../docs/graphs/besmettingen-leeftijd-"+str(lastDays)+".svg", format="svg")
    else:
        plt.savefig("../docs/graphs/besmettingen-leeftijd.svg", format="svg")

    dateCache.cacheReport()

if __name__ == '__main__':
    sys.exit(main())