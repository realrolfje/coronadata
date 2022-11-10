#!/usr/bin/env python3
#
from http.client import CannotSendRequest
from matplotlib import pyplot as plt
import modules.brondata as brondata
import modules.arguments as arguments
from modules.brondata import decimalstring, intOrZero, dateCache, smooth, double_savgol
from modules.datautil import anotate, runIfNewData
from datetime import datetime, date, timedelta
import sys

def main():
    runIfNewData(__file__)
    metenisweten = brondata.readjson('../cache/daily-stats.json')
    varianten = brondata.readjson('../cache/COVID-19_varianten.json')
    createVariantenGraph(metenisweten, varianten)

def createVariantenGraph(metenisweten, varianten):
    varianten_map = {
        # datum : {
        #     code : {
        #       cases: 0,
        #       size: 0
        #     }
        # }
    }

    varianten_totaal = {
        'x': [],
        # 'variant code' : percentage
        'totaal': [],
    }

    opnamekans = {
        'x': [],
        'kans':[]    
    }

    # Build unique complete set of variant codes and add add array placeholders

    # https://en.wikipedia.org/wiki/Greek_alphabet
    namefix = {
        "Omicron" : "Omikron"
    }

    # Get all id's and names of the variants and put them in variantcodes
    variantcodes = {}
    for record in varianten:
        if record['Variant_code'] not in variantcodes:
            varianten_totaal[record['Variant_code']] = []
            if record['Variant_name'] == '':
                variantcodes[record['Variant_code']] = record['Variant_code']
            elif record['Variant_name'] in namefix:
                variantcodes[record['Variant_code']] = "%s (%s)" % (namefix[record['Variant_name']], record['Variant_code'])
            else:
                variantcodes[record['Variant_code']] = "%s (%s)" % (record['Variant_name'], record['Variant_code'])
            print('Variant: %s' % variantcodes[record['Variant_code']])

    varianten_totaal['onbekend'] = []
    variantcodes['onbekend'] = "Onbekend"

    # Get variant percentages per day and put them in "varianten_map[date][variantcode] = {cases, size}"
    for record in varianten:
        if record.get('May_include_samples_listed_before', False):
            continue

        d = record['Date_of_statistics_week_start']
        c = record['Variant_code']

        if d not in varianten_map:
            varianten_map[d] = {}

        if c not in varianten_map[d]:
            varianten_map[d][c] = {}

        varianten_map[d][c]['cases'] = record['Variant_cases']
        varianten_map[d][c]['size'] = record['Sample_size']

        if varianten_map[d][c]['cases'] >varianten_map[d][c]['size']:
            print(record)
            sys.exit(1)

    # Take al variant percentages and multiply them with the actual number of sick people on that day
    for key in varianten_map:
        # workaround for a day where variant data was not available
        if key == "2022-09-26":
            continue

        varianten_totaal['x'].append(dateCache.parse(key))

        # For each variant, determine the number of sick people (variant percentage times estimate)
        geschat_ziek = metenisweten[key]['rolf_besmettelijk']

        if geschat_ziek is None:
            print("Niks geschat ziek op %s" % key)
            geschat_ziek = 0
            # continue

        # Sample size is niet het totaal aantal cases, dus om de percentages goed te berekenen
        # tellen we alle cases bijelkaar op (dat is dan 100%). De aanname is hierbij dat iemand
        # maar 1 variant onder de leden kan hebben.
        totaal_cases = 0
        for variantcode in varianten_map[key]:
            totaal_cases += varianten_map[key][variantcode]['cases']

        totaal_percentage = 0
        for variantcode in variantcodes.keys():
            if variantcode == 'onbekend':
                continue

            if variantcode in varianten_map[key]:
                # percentage = varianten_map[key][variantcode]['cases']/varianten_map[key][variantcode]['size']
                percentage = varianten_map[key][variantcode]['cases']/totaal_cases
                # print("cases = %d, size =%d, percentage = %.2f" %(varianten_map[key][variantcode]['cases'], varianten_map[key][variantcode]['size'], percentage))
            else:
                print("Variant niet in map: %s" % variantcode)
                percentage = 0
            totaal_percentage += percentage
            varianten_totaal[variantcode].append(percentage * geschat_ziek)


        # print("Totaal percentage varianten: %.2f" % totaal_percentage)
        if totaal_percentage > 2:
            sys.exit(1)

        # If percentage does not add up to 1 (100%), add this as "onbekend" (unknown)    
        gap = max(0,(1 - totaal_percentage) * geschat_ziek)
        # print("Variant onbekend gap : %.2f" % gap)
        varianten_totaal['onbekend'].append(gap)
        if gap > 0:
            print('Percentages niet compleet voor %s, onbekend: %d' % (key, gap))

    date_range = brondata.getDateRange(metenisweten)
    lastDays = arguments.lastDays()
    if (lastDays>0):
        date_range = date_range[-lastDays:]


    # Create a list of total number of sick people per day to plot a totals line over the graph
    totaal_ziek = {
        'x':[],
        'y':[],
    }
    for k in date_range:
        key = k.strftime('%Y-%m-%d')
        if key in metenisweten and metenisweten[key]['rolf_besmettelijk']:
            totaal_ziek['x'].append(k)
            totaal_ziek['y'].append(metenisweten[key]['rolf_besmettelijk'])
            
        weeklater = (dateCache.parse(key) + timedelta(days=7)).strftime('%Y-%m-%d')

        # Calculate the number of infections against hospitalization
        if weeklater in metenisweten and metenisweten[weeklater]['nu_opgenomen'] and metenisweten[weeklater]['nu_op_ic'] and metenisweten[weeklater]['rolf_besmettelijk']:
            kans = 100 * (metenisweten[weeklater]['nu_opgenomen'] + metenisweten[weeklater]['nu_op_ic']) / metenisweten[weeklater]['rolf_besmettelijk']
            opnamekans['x'].append(dateCache.parse(weeklater))
            opnamekans['kans'].append(kans)


    # Find when a variant becomes dominant
    dominance = []
    for i in range(len(varianten_totaal['x'])):
        n = 0
        dominant = ''
        for code in variantcodes:
            if varianten_totaal[code][i] > n:
                n = varianten_totaal[code][i]
                dominant = code
        dominance.append(dominant)

    # top 10:
    totals = {}
    for code in variantcodes:
        totals[code] = sum(varianten_totaal[code])    
    totals=dict(sorted(totals.items(),key=lambda x:x[1]))
    top_variants=[]
    for k in totals.keys(): top_variants.append(k)
    top_variants=top_variants[-5:]

    print("Top variants are: %s" % top_variants)

    varianten_totaal['overig'] = [0] * len(varianten_totaal['x'])
    varianten_totaal['totaal'] = [0] * len(varianten_totaal['x'])
    for key in variantcodes:
        varianten_totaal['totaal'] = [ x + y for x,y in zip(varianten_totaal['totaal'], varianten_totaal[key])]
        if key not in top_variants and key != 'x' and key != 'totaal':
            varianten_totaal['overig'] = [ x + y for x,y in zip(varianten_totaal['overig'], varianten_totaal[key])]
            varianten_totaal.pop(key, None)

    # record['Variant_code'],
    # record['Variant_name'],
    # record['ECDC_category'],
    # record['WHO_category'],
    # record['May_include_samples_listed_before'],
    # record['Sample_size'],
    # record['Variant_cases']

    print('Generating variants graph...')
    fig, ax1 = plt.subplots(figsize=(10, 5))
    fig.subplots_adjust(top=0.92, bottom=0.13, left=0.09, right=0.91)

    ax1.grid(which='both', axis='both', linestyle='-.',
            color='gray', linewidth=1, alpha=0.3)

    ax1.set_xlabel("Datum")
    ax1.set_ylabel("Geschat aantal personen ziek")

    ax2 = plt.twinx()
    ax2.set_ylabel("Opnamekans")

    # Variants in order of today's highest
    today = {}
    for code in varianten_totaal:
        if code != 'x':
            today[code] = varianten_totaal[code][-1]
    today=dict(sorted(today.items(),key=lambda x:x[1]))

    yrray = []
    ylabels = []

    # yrray.append(varianten_totaal['totaal'])
    # ylabels.append('Totaal')

    yrray.append(varianten_totaal['overig'])
    ylabels.append("Overig (nu: %s)" % (decimalstring(round(varianten_totaal['overig'][-1]))))

    for code in today:
        if code in varianten_totaal and code in variantcodes:
            yrray.append(varianten_totaal[code])
            ylabels.append("%s (nu: %s)" % (variantcodes[code],decimalstring(round(varianten_totaal[code][-1]))))

    ax1.stackplot(
        varianten_totaal['x'],
        *yrray,
        labels=ylabels,
        colors=( # note these are in reverse order because we revert the labels later
            'gray',
            'limegreen',
            'yellow',
            # 'darkorange',
            'mediumslateblue',
            'tomato',
            'deepskyblue',
        ),
        baseline='zero'
    )

    ax1.plot(
        totaal_ziek['x'],
        totaal_ziek['y'],
        color='steelblue',
        linestyle=':', 
        label='Totaal (nu: %s)' % decimalstring(round(totaal_ziek['y'][-1]))
    )


    # smoothkans = opnamekans['kans']
    # smoothkans = smooth(opnamekans['kans'])
    smoothkans = double_savgol(opnamekans['kans'], 2, 7, 1)

    ax2.plot(opnamekans['x'], 
            smoothkans, 
            color='darkblue',
            linestyle='--', 
            label='Opnamekans bij besmetting (nu: %s%%)' % decimalstring(round(smoothkans[-1],1)),
            alpha=0.7)


    # print('reversed %s' % ax1.legend().legendHandles)
    # totaal_prikken = decimalstring(vaccins_delta['totaal'][-1])

    # ax1.plot(vaccins_delta['x'], 
    #          vaccins_delta['totaal'], 
    #          color='black',
    #          label='Totaal per dag (nu: %s)' % totaal_prikken)


    for i in range(len(dominance)):
        if i > 1  and dominance[i] != dominance[i-1]:

            ax1.annotate(
                "%s\nDominant:\n%s" % (varianten_totaal['x'][i].strftime("%Y-%m-%d"), variantcodes.get(dominance[i], dominance[i])),
                xy=(varianten_totaal['x'][i], varianten_totaal['totaal'][i]),
                xytext=(varianten_totaal['x'][i], varianten_totaal['totaal'][i] + 200000),
                fontsize=8,
                bbox=dict(boxstyle='round,pad=0.4', fc='ivory', alpha=0.7),
                ha='center',
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.1')
            )
    

    # graphname='variants'
    # for event in events:
    #     if graphname in event \
    #         and dateCache.parse(event[graphname][0]) > date_range[0]\
    #         and (len(event[graphname]) <= 2 or len(date_range) <= event[graphname][2]):
    #         anotate(
    #             ax1, 
    #             vaccins_delta['x'], vaccins_delta['totaal'],
    #             event['date'], event['event'], 
    #             event[graphname][0], 
    #             event[graphname][1]
    #         )

    # Put vertical line at current day
    plt.text(
        x=dateCache.today(),
        y=0,
        s=datetime.now().strftime("%d"), 
        color="white",
        fontsize=8,
        ha="center",
        va="center",
        bbox=dict(boxstyle='round,pad=0.1', facecolor='red', alpha=1, edgecolor='red'),
        zorder=10
    )
    plt.axvline(dateCache.today(), color='red', linewidth=0.5)
    plt.gca().set_xlim([date_range[0], date_range[-1]])

    ax1.set_ylim([0, 2000000])
    ax1.set_yticks      ([ 200000, 400000, 600000, 800000, 1000000, 1200000,1400000,1600000,1800000])
    ax1.set_yticklabels([  '200k', '400k', '600k', '800k',  '1.0M',  '1.2M', '1.4M', '1.6M', '1.8M'])

    ax2.set_ylim([0, 2.5])
    ax2.set_yticks      ([ 0.5,    1,     1.5,    2,      2.5])
    ax2.set_yticklabels([ '0.5%', '1.0%','1.5%', '2.0%', '2.5%'])

    gegenereerd_op=datetime.now().strftime("%Y-%m-%d %H:%M")
    data_tot=varianten_totaal['x'][-1].strftime("%Y-%m-%d")
    filedate=data_tot

    plt.title('Besmettelijke personen per COVID-19 variant')

    footerleft="Gegenereerd op "+gegenereerd_op+", o.b.v. data tot "+data_tot+".\nSource code: http://github.com/realrolfje/coronadata"
    plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")


    footerright="Publicatiedatum RIVM "+filedate+".\nBron: https://data.rivm.nl/covid-19/COVID-19_varianten.json + besmettingdata"
    plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

    # Reverse sort the legend and place upper left
    handles, labels = ax1.get_legend_handles_labels()   #get the handles
    ax1.legend(reversed(handles), reversed(labels), loc="upper left")

    ax2.legend(loc="upper right")


    if (lastDays > 0):
        plt.savefig("../docs/graphs/variants-"+str(lastDays)+".svg", format="svg")
    else:
        plt.savefig("../docs/graphs/variants.svg", format="svg")

    dateCache.cacheReport()


if __name__ == '__main__':
    sys.exit(main())