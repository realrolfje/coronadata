#!/usr/bin/env python3
#
from http.client import CannotSendRequest
from matplotlib import pyplot as plt
import modules.brondata as brondata
import modules.arguments as arguments
from modules.brondata import decimalstring, printDict, intOrZero, dateCache, smooth, double_savgol, logError
from modules.defaults import CACHE_DIR, DAILY_STATS, GRAPHS_DIR, VARIANT_TAXONOMY
from modules.buildtime import reference_datetime
from modules.datautil import anotate, place_label, runIfNewData
from pipeline.variant_taxonomy import (
    load_taxonomy,
    make_exclusive_week,
    pool_exclusive_weeks,
)
from pipeline.chart_scale import compact_number, confirmed_dominance, nice_axis_scale
from datetime import datetime, date, timedelta
import sys

def main():
    # runIfNewData(__file__)
    metenisweten = brondata.readjson(DAILY_STATS)
    varianten = brondata.readjson(CACHE_DIR / 'COVID-19_varianten.json')
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
    week_records = {}
    invalid_weeks = set()

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
            if record['Variant_code'] == 'Recombinants':
                variantcodes[record['Variant_code']] = "Overige recombinanten"
            elif record['Variant_name'] == '':
                variantcodes[record['Variant_code']] = record['Variant_code']
            elif record['Variant_name'] in namefix:
                variantcodes[record['Variant_code']] = "%s (%s)" % (
                    namefix[record['Variant_name']], record['Variant_code']
                )
            elif record['Variant_name'] == record['Variant_code']:
                variantcodes[record['Variant_code']] = record['Variant_code']
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
        week_records.setdefault(d, []).append(record)

        if d not in varianten_map:
            varianten_map[d] = {}

        if c not in varianten_map[d]:
            varianten_map[d][c] = {}

        varianten_map[d][c]['cases'] = record['Variant_cases']
        varianten_map[d][c]['size'] = record['Sample_size']
        varianten_map[d][c]['sub_of'] = record['Is_subvariant_of']
        varianten_map[d][c]['prevalence'] = record['Variant_cases']/record['Sample_size']


        # if d == '2023-02-13':
        #     print('%s, %s prevalence %.2f (is variant of : %s) samples:%d cases:%d' %(d, c, varianten_map[d][c]['prevalence'], record['Is_subvariant_of'], varianten_map[d][c]['size'], varianten_map[d][c]['cases']))

        if varianten_map[d][c]['cases'] > varianten_map[d][c]['size']:
            logError(
                f"Variantenweek {d} overgeslagen: variant {c} heeft "
                f"{varianten_map[d][c]['cases']} gevallen bij een steekproef "
                f"van {varianten_map[d][c]['size']}."
            )
            invalid_weeks.add(d)
    
    print(f"Last week date with varianten: {d}")
    
    # print("-----")
    # printDict(varianten_map['2023-02-13'])
    # print("-----")


    taxonomy = load_taxonomy(VARIANT_TAXONOMY)
    exclusive_weeks = []
    for d, variants_for_week in varianten_map.items():
        if d in invalid_weeks:
            continue
        try:
            exclusive = make_exclusive_week(week_records[d], taxonomy)
        except ValueError as error:
            logError(f"Variantenweek {d} overgeslagen: {error}")
            invalid_weeks.add(d)
            continue
        if exclusive.unresolved_parents:
            logError(
                f"Variantenweek {d} overgeslagen door onopgeloste variantouders: "
                + ", ".join(exclusive.unresolved_parents)
            )
            invalid_weeks.add(d)
            continue
        exclusive_weeks.append(exclusive)

    for d in invalid_weeks:
        varianten_map.pop(d, None)

    pooled_weeks = {
        week.date: week
        for week in pool_exclusive_weeks(
            exclusive_weeks, window_weeks=4, minimum_samples=20
        )
    }
    rolling_samples = {}
    for d in list(varianten_map):
        pooled = pooled_weeks.get(d)
        if pooled is None:
            varianten_map.pop(d)
            continue
        rolling_samples[d] = pooled.sample_size
        for code, variant in varianten_map[d].items():
            variant['cases'] = pooled.counts.get(code, 0)
            variant['size'] = pooled.sample_size
            variant['prevalence'] = variant['cases'] / pooled.sample_size

    print(
        f"Variantpercentages exclusief gemaakt met {taxonomy.version} en "
        f"gewogen over vier weken (minimaal 20 monsters); "
        f"laatste venster: {max(pooled_weeks)}, n={rolling_samples[max(pooled_weeks)]}"
    )

    # print("-----")
    # printDict(varianten_map['2023-02-13'])
    # print("-----")    

    # Take al variant percentages and multiply them with the actual number of sick people on that day
    previous_variant_date = None
    for key in sorted(varianten_map):
        # For each variant, determine the number of sick people (variant percentage times estimate)
        if metenisweten.get(key, None) is None:
            print("Geen data over besmettelijkheid %s" % key)
            continue

        geschat_ziek = metenisweten[key]['rolf_besmettelijk']

        if geschat_ziek is None:
            print("Niks geschat ziek op %s" % key)
            continue

        current_variant_date = dateCache.parse(key)
        if (
            previous_variant_date is not None
            and current_variant_date - previous_variant_date > timedelta(days=8)
        ):
            # A NaN observation prevents matplotlib from drawing a straight line
            # across periods with fewer than twenty pooled samples.
            varianten_totaal['x'].append(previous_variant_date + timedelta(days=7))
            for variantcode in variantcodes:
                varianten_totaal[variantcode].append(float('nan'))
        previous_variant_date = current_variant_date

        # Add following data to the graph.
        varianten_totaal['x'].append(current_variant_date)

        totaal_percentage = 0
        for variantcode in variantcodes.keys():
            if variantcode == 'onbekend':
                continue

            if variantcode in varianten_map[key]:
                percentage = varianten_map[key][variantcode]['prevalence']
            else:
                print("Variant niet in map: %s" % variantcode)
                percentage = 0

            if percentage < 0:
                logError('Error %s %s %.3f' % (key, variantcode, percentage))
            
            totaal_percentage += percentage
            varianten_totaal[variantcode].append(percentage * geschat_ziek)


        if totaal_percentage > 1.000001:
            logError(
                "Variantenweek %s overgeslagen: exclusief totaal is %.2f%%."
                % (key, totaal_percentage * 100)
            )
            varianten_totaal['x'].pop()
            for variantcode in variantcodes.keys():
                if variantcode != 'onbekend':
                    varianten_totaal[variantcode].pop()
            continue


        # If percentage does not add up to 1 (100%), add this as "onbekend" (unknown)    
        gap = max(0,(1 - totaal_percentage) * geschat_ziek)
        # A positive remainder is expected when the RIVM sample contains sequences
        # that are not represented by one of the published variant categories. It is
        # plotted as "Onbekend" and is not a taxonomy/build warning. Negative
        # residuals, unresolved parents and totals above the sample size are already
        # rejected and logged while constructing the exclusive weeks above.
        varianten_totaal['onbekend'].append(gap)

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
        else:
            print(f"{key} not in metenisweten or not rolf_besmettelijk")
            
        weeklater = (dateCache.parse(key) + timedelta(days=7)).strftime('%Y-%m-%d')

        weeklater_opgenomen = metenisweten.get(weeklater, {}).get('nu_opgenomen')
        if not weeklater_opgenomen:
            print("Geen opnames op {weeklater}")
            continue

        weeklater_op_ic = metenisweten.get(weeklater, {}).get('nu_op_ic')
        if not weeklater_op_ic:
            print("Geen ic opnames op {weeklater}")
            continue

        weeklater_rolf_besmettelijk = metenisweten.get(weeklater, {}).get('rolf_besmettelijk')
        if not weeklater_rolf_besmettelijk:
            print("Geen besmettelijk berekening op {weeklater}")
            continue

        # Calculate the number of infections against hospitalization
        kans = 100 * (weeklater_opgenomen + weeklater_op_ic) / weeklater_rolf_besmettelijk
        opnamekans['x'].append(dateCache.parse(weeklater))
        opnamekans['kans'].append(kans)


    # Find candidates above 50%; dominance is only confirmed after two
    # consecutive qualifying pooled windows.
    dominance_candidates = []
    for i in range(len(varianten_totaal['x'])):
        n = 0
        dominant = ''
        total = sum(
            varianten_totaal[code][i]
            for code in variantcodes
            if varianten_totaal[code][i] == varianten_totaal[code][i]
        )
        for code in variantcodes.keys():
            if code == 'onbekend':
                continue
            # print("%s %d" %(code, varianten_totaal[code][i]))
            if varianten_totaal[code][i] > n:
                n = varianten_totaal[code][i]
                dominant = code
        if total <= 0 or n / total <= 0.5:
            dominant = ''
        dominance_candidates.append(dominant)
    dominance = confirmed_dominance(dominance_candidates)


    visible_indices = [
        index
        for index, observation_date in enumerate(varianten_totaal['x'])
        if date_range[0] <= observation_date <= date_range[-1]
    ]
    visible_dominance = [
        dominance[index] for index in visible_indices if dominance[index]
    ]

    # Only retain variants that matter in the visible graph. Previously the
    # 365-day graph included every variant that had ever been dominant.
    top_variants = set(visible_dominance)
    if any(
        varianten_totaal['onbekend'][index] > 0 for index in visible_indices
    ):
        top_variants.add('onbekend')

    print("Variants which became dominant: %s" % top_variants)

    # # top 3 all time:
    totals = {}
    # for code in variantcodes:
    #     totals[code] = sum(varianten_totaal[code])    
    # totals=dict(sorted(totals.items(),key=lambda x:x[1]))
    # print(totals)
    # top_variants=[]
    # for k in totals.keys(): top_variants.append(k)
    # top_variants=top_variants[-3:]

    if not visible_indices:
        raise ValueError(
            "No variant data between %s and %s; newest variant week is %s. "
            "Run scripts/updateActiveSources.py rivm_variants."
            % (date_range[0].date(), date_range[-1].date(), varianten_totaal['x'][-1].date())
        )

    # Add the five largest variants at the end of the visible period.
    latest_visible_index = visible_indices[-1]
    for code in variantcodes:
        totals[code] = varianten_totaal[code][latest_visible_index]
    totals=dict(sorted(totals.items(),key=lambda x:x[1]))
    top_variants.update(list(totals.keys())[-5:])

    print("Top variants including dominants are: %s" % top_variants)
    varianten_totaal['overig'] = [0] * len(varianten_totaal['x'])
    varianten_totaal['totaal'] = [0] * len(varianten_totaal['x'])
    for key in variantcodes:
        varianten_totaal['totaal'] = [ x + y for x,y in zip(varianten_totaal['totaal'], varianten_totaal[key])]
        if key not in top_variants and key != 'x' and key != 'totaal':
            varianten_totaal['overig'] = [ x + y for x,y in zip(varianten_totaal['overig'], varianten_totaal[key])]
            varianten_totaal.pop(key, None)

    visible_values = [
        value
        for observation_date, value in zip(
            varianten_totaal['x'], varianten_totaal['totaal']
        )
        if date_range[0] <= observation_date <= date_range[-1]
    ]
    visible_values.extend(
        value
        for observation_date, value in zip(totaal_ziek['x'], totaal_ziek['y'])
        if date_range[0] <= observation_date <= date_range[-1]
    )
    y_maximum, y_step = nice_axis_scale(visible_values)
    y_ticks = [
        index * y_step
        for index in range(int(round(y_maximum / y_step)) + 1)
    ]

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
            'purple',
            'yellow',
            'darkorange',
            'brown',
            'blue',
            'tomato',
            'deepskyblue'
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
    if opnamekans['kans']:
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


    # Reverse sort the legend and place upper left
    handles, labels = ax1.get_legend_handles_labels()   #get the handles
    if lastDays > 0:
        legends = [ax1.legend(reversed(handles), reversed(labels), loc="upper left")]
    else:
        legends = [ax1.legend(reversed(handles), reversed(labels), loc="upper left", ncol=2, fontsize=7)]

    if opnamekans['kans']:
        legends.append(ax2.legend(loc="upper right"))

    ax1.set_xlim([date_range[0], date_range[-1]])
    ax1.set_ylim([0, y_maximum])
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    plot_area = ax1.get_window_extent(renderer)
    occupied = [legend.get_window_extent(renderer) for legend in legends]

    annotated_variants = set()
    first_visible_index = visible_indices[0]
    initial_dominant = (
        dominance[first_visible_index - 1] if first_visible_index > 0 else ''
    )
    for i in visible_indices:
        dominant = dominance[i]
        if dominant and dominant not in annotated_variants:
            annotated_variants.add(dominant)
            is_initial_dominant = dominant == initial_dominant
            annotation_x = varianten_totaal['x'][i]
            if is_initial_dominant:
                annotation_x = min(
                    annotation_x + timedelta(days=120), date_range[-1]
                )
                annotation_text = "%s al dominant\nbij begin periode" % (
                    variantcodes.get(dominant, dominant)
                )
            else:
                annotation_text = "%s dominant\n%s" % (
                    variantcodes.get(dominant, dominant),
                    varianten_totaal['x'][i].strftime("%Y-%m-%d"),
                )

            occupied.append(place_label(
                ax1, renderer, plot_area, occupied, annotation_text,
                (varianten_totaal['x'][i], varianten_totaal['totaal'][i]),
                annotation_x, y_maximum,
            ))
    

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
        s=reference_datetime(metenisweten).strftime("%d"),
        color="white",
        fontsize=8,
        ha="center",
        va="center",
        bbox=dict(boxstyle='round,pad=0.1', facecolor='red', alpha=1, edgecolor='red'),
        zorder=10
    )
    plt.axvline(dateCache.today(), color='red', linewidth=0.5)
    plt.gca().set_xlim([date_range[0], date_range[-1]])

    ax1.set_ylim([0, y_maximum])
    ax1.set_yticks(y_ticks)
    ax1.set_yticklabels([compact_number(value) for value in y_ticks])

    ax2.set_ylim([0, 2.0])
    ax2.set_yticks      ([ 0.5,    1,     1.5,    2,   ])
    ax2.set_yticklabels([ '0.5%', '1.0%','1.5%', '2.0%'])

    gegenereerd_op=reference_datetime(metenisweten).strftime("%Y-%m-%d %H:%M")
    data_tot=varianten_totaal['x'][-1].strftime("%Y-%m-%d")
    filedate=data_tot

    plt.title('Besmettelijke personen per COVID-19 variant')

    footerleft="Gegenereerd op "+gegenereerd_op+", o.b.v. data tot "+data_tot+".\nSource code: http://github.com/realrolfje/coronadata"
    plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")


    latest_sample_size = rolling_samples[data_tot]
    footerright=(
        "Publicatiedatum RIVM " + filedate + ". "
        "Variantverdeling: gewogen over 4 weken (n="
        + str(latest_sample_size) + ").\n"
        "Bron: https://data.rivm.nl/covid-19/COVID-19_varianten.json + besmettingdata"
    )
    plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")


    if (lastDays > 0):
        filename = GRAPHS_DIR / ("variants-"+str(lastDays)+".svg")
    else:
        filename = GRAPHS_DIR / "variants.svg"
    
    print(f"Saving to {filename}")
    plt.savefig(filename, format="svg")

    dateCache.cacheReport()


if __name__ == '__main__':
    sys.exit(main())
