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
from modules.defaults import DAILY_STATS, DATA_DIR, GRAPHS_DIR
from modules.buildtime import build_datetime
from modules.datautil import runIfNewData, anotate
import csv
from pathlib import Path
import sys


LCPS_HANDOFF_DATE = datetime.date(2024, 1, 2)


def merge_lcps_history(metenisweten, filename=None):
    """Return a graph-only copy extended with LCPS occupancy after NICE ended."""
    filename = Path(filename or (Path(__file__).resolve().parents[1] / "cache/covid-19-datafeed.csv"))
    merged = dict(metenisweten)
    if not filename.exists():
        return merged
    with filename.open(newline="", encoding="utf-8-sig") as source_file:
        for row in csv.DictReader(source_file):
            date = datetime.datetime.strptime(row["datum"], "%d-%m-%Y").date()
            if date < LCPS_HANDOFF_DATE or date > datetime.date(2024, 5, 31):
                continue
            key = date.isoformat()
            record = dict(merged.get(key, {}))
            record["nu_op_ic"] = int(row["IC_bezetting_covid"])
            record["nu_opgenomen"] = int(row["kliniek_bezetting_covid"])
            merged[key] = record
    return dict(sorted(merged.items()))

def main():
    runIfNewData(__file__)
    metenisweten = brondata.readjson(DAILY_STATS)
    events = brondata.readjson(DATA_DIR / 'measures-events.json')
    createZiekGraph(metenisweten, events)


def select_date_range(metenisweten, last_days):
    """Keep the short hospital chart anchored to its final reported observation."""
    dates = brondata.getDateRange(metenisweten)
    hospital_dates = [
        d for d in dates
        if metenisweten.get(d.strftime("%Y-%m-%d"), {}).get("nu_opgenomen")
        or metenisweten.get(d.strftime("%Y-%m-%d"), {}).get("nu_op_ic")
    ]
    if hospital_dates:
        final_hospital_date = hospital_dates[-1]
        dates = [date for date in dates if date <= final_hospital_date]
    return dates[-last_days:] if last_days > 0 else dates

def createZiekGraph(metenisweten, events):
    graphname="zieken"

    print("Calculating "+graphname+" graph...")
    metenisweten = merge_lcps_history(metenisweten)

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

    lastDays = arguments.lastDays()
    date_range = select_date_range(metenisweten, lastDays)

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

    # The archived chart is deliberately limited to hospital occupancy. The old
    # prevalence estimate and measure annotations describe a different metric.
    ax1.grid(which='both', axis='both', linestyle='-.',
            color='gray', linewidth=1, alpha=0.3)


    if opgenomen['y']:
        nu_opgenomen = opgenomen['y'][-1]
        ax1.plot(opgenomen['x'], opgenomen['y'], color='orange', label='aantal op verpleegafdeling (laatste: '+decimalstring(nu_opgenomen)+')')
        ax1.plot(opgenomen_voorspeld['x'], opgenomen_voorspeld['y'], color='orange', linestyle=':')


    if ic['y']:
        nu_op_ic = ic['y'][-1]
        ax1.plot(ic['x'], ic['y'], color='red', label='aantal op IC (laatste: '+decimalstring(nu_op_ic)+')')
        ax1.plot(ic_voorspeld['x'], ic_voorspeld['y'], color='red', linestyle=':')

    # Mark the final day represented by this chart. For an ended historical series this is
    # deliberately not the wall-clock date.
    chart_end = date_range[-1]
    plt.text(
        x=chart_end,
        y=0,
        s=chart_end.strftime("%d"),
        color="white",
        fontsize=8,
        ha="center",
        va="center",
        bbox=dict(boxstyle='round,pad=0.1', facecolor='red', alpha=1, edgecolor='red'),
        zorder=10
    )
    plt.axvline(chart_end, color='red', linewidth=0.5)

    # Horizontale lijn om te checken waar we de IC opnames mee kunnen vergelijken
    if ic['y']:
        ax1.axhline(ic['y'][-1], color='red', linestyle=(0, (5, 30)), linewidth=0.2)

    ax1.set_xlabel("Datum")
    ax1.set_ylabel("Aantal op verpleegafdeling / op IC")

    ax1.set_ylim([0, 3000])

    plt.gca().set_xlim([date_range[0], date_range[-1]])
    if date_range[0].date() <= LCPS_HANDOFF_DATE <= date_range[-1].date():
        ax1.axvline(LCPS_HANDOFF_DATE, color="gray", linewidth=0.8, linestyle="--")
        ax1.text(
            LCPS_HANDOFF_DATE, 2875, "vanaf hier LCPS", rotation=90,
            va="top", ha="right", fontsize=7, color="gray"
        )

    gegenereerd_op=build_datetime().strftime("%Y-%m-%d %H:%M")
    available_dates = opgenomen['x'] + ic['x']
    data_tot=max(available_dates).strftime("%Y-%m-%d")

    plt.title('Historische COVID-19-bezetting in ziekenhuis en IC')

    footerleft="Gegenereerd op "+gegenereerd_op+", o.b.v. data tot "+data_tot+".\nSource code: http://github.com/realrolfje/coronadata"
    plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")

    footerright="Historische reeks beëindigd op 31-05-2024.\nBronnen: RIVM/NICE; vanaf 02-01-2024 LCPS-datafeed."
    plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

    ax1.legend(loc="upper left")

    if (lastDays > 0):
        plt.savefig(GRAPHS_DIR / (graphname+"-"+str(lastDays)+".svg"), format="svg")
    else:
        plt.savefig(GRAPHS_DIR / (graphname+".svg"), format="svg")

    dateCache.cacheReport()

if __name__ == '__main__':
    sys.exit(main())
