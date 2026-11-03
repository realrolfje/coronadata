#!/usr/bin/env python3

from datetime import date, datetime, timedelta
import sys

from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter, MonthLocator

import modules.arguments as arguments
import modules.brondata as brondata
from modules.defaults import CACHE_DIR, DATA_DIR, GRAPHS_DIR
from modules.buildtime import reference_datetime
from modules.datautil import anotate
from pipeline.erviss import parse as parse_erviss
from pipeline.weekly_trend import parser as weekly_trend_parser
from createSariGraph import nice_maximum


# This is the first week shown in the full chart.
START_DATE = date(2023, 3, 13)

parse_detections = weekly_trend_parser(
    "rivm_laboratory_sars_cov_2_detections",
    "laboratory_sars_cov_2_detections_weekly",
    "positive_samples_per_week",
)
parse_percentage = weekly_trend_parser(
    "rivm_laboratory_sars_cov_2_positive",
    "laboratory_sars_cov_2_positive_percentage",
    "percent_of_tested_samples",
)


def weekly_series(result, cutoff):
    observations = sorted(result.observations, key=lambda item: item.date)
    dates = [date.fromisoformat(item.date) for item in observations]
    return (
        [day for day in dates if day >= cutoff],
        [item.value for day, item in zip(dates, observations) if day >= cutoff],
    )


def createLaboratoriumGraph(
    events, detections_file=None, percentage_file=None, erviss_file=None,
):
    detections_file = detections_file or (CACHE_DIR / "rivm-laboratory-sars-cov-2-detections-weekly.csv")
    percentage_file = percentage_file or (CACHE_DIR / "rivm-laboratory-sars-cov-2-positive-weekly.csv")
    erviss_file = erviss_file or (CACHE_DIR / "ecdc-erviss-non-sentinel-tests-detections.csv")

    detections = parse_detections(detections_file)
    final_date = date.fromisoformat(detections.newest_observation)
    last_days = arguments.lastDays()
    cutoff = final_date - timedelta(days=last_days) if last_days > 0 else START_DATE

    rivm_dates, rivm_values = weekly_series(detections, cutoff)
    percentage_dates, percentage_values = weekly_series(parse_percentage(percentage_file), cutoff)
    erviss_dates, erviss_values = weekly_series(parse_erviss(erviss_file), cutoff)

    fig, ax1 = plt.subplots(figsize=(10, 5))
    fig.subplots_adjust(top=0.92, bottom=0.16, left=0.09, right=0.91)
    ax2 = ax1.twinx()

    ax1.bar(rivm_dates, rivm_values, width=5, color="steelblue", alpha=0.6,
            label=f"Positieve monsters per week, RIVM (laatste: {int(rivm_values[-1])})")
    ax1.plot(erviss_dates, erviss_values, color="purple", linewidth=1.5,
             label=f"Positieve monsters per week, ECDC ERVISS (laatste: {int(erviss_values[-1])})")
    ax2.plot(percentage_dates, percentage_values, color="darkorange", linewidth=2,
             label=f"Percentage positief, RIVM, rechteras (laatste: {percentage_values[-1]:.1f}%)")

    ax1.grid(which="both", axis="both", linestyle="-.", color="gray", linewidth=1, alpha=0.3)
    ax1.set_ylim(0, nice_maximum(max(rivm_values + erviss_values) * 1.08))
    ax2.set_ylim(0, nice_maximum(max(percentage_values) * 1.08))
    ax1.set_xlim(
        min(rivm_dates[0], erviss_dates[0]) - timedelta(days=4),
        final_date + timedelta(days=4),
    )
    ax1.set_ylabel("Aantal positieve monsters per week")
    ax2.set_ylabel("Percentage positieve monsters")
    ax1.set_xlabel("Week")
    ax1.set_title("Positieve laboratoriummonsters SARS-CoV-2 in Nederland")
    ax1.xaxis.set_major_locator(MonthLocator(interval=2 if last_days > 0 else 4))
    ax1.xaxis.set_major_formatter(DateFormatter("%Y-%m"))

    erviss_datetimes = [datetime.combine(day, datetime.min.time()) for day in erviss_dates]
    for event in events:
        if 'laboratoriumloc' in event:
            anotate(
                ax1,
                erviss_datetimes,
                erviss_values,
                event['date'], event['event'],
                event['laboratoriumloc'][0],
                event['laboratoriumloc'][1] * ax1.get_ylim()[1]
            )

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc="upper right", fontsize=8)

    generated = reference_datetime({final_date.isoformat(): {}}).strftime("%Y-%m-%d %H:%M")
    fig.text(0.01, 0.025, f"Gegenereerd op {generated}, data t/m week van {final_date}.\nSource code: http://github.com/realrolfje/coronadata",
             ha="left", fontsize=8, color="gray")
    fig.text(0.99, 0.025, "Bron: RIVM virologische weekstaten (NWKV) en ECDC ERVISS.",
             ha="right", fontsize=8, color="gray")

    suffix = f"-{last_days}" if last_days > 0 else ""
    plt.savefig(GRAPHS_DIR / f"laboratorium{suffix}.svg", format="svg")
    plt.close(fig)


if __name__ == "__main__":
    createLaboratoriumGraph(brondata.readjson(DATA_DIR / 'measures-events.json'))
    sys.exit(0)
