#!/usr/bin/env python3

import math
import sys

from matplotlib import pyplot as plt

import modules.arguments as arguments
import modules.brondata as brondata
from modules.defaults import CACHE_DIR, DAILY_STATS, GRAPHS_DIR
from modules.buildtime import build_datetime
from pipeline.sari import parse


def nice_maximum(value):
    if value <= 0:
        return 10
    magnitude = 10 ** math.floor(math.log10(value))
    for step in (1, 2, 2.5, 5, 10):
        candidate = step * magnitude
        if candidate >= value:
            return candidate
    return 10 * magnitude


def createSariGraph(metenisweten, filename=None):
    filename = filename or (CACHE_DIR / "rivm-nice-sari-weekly-admissions.csv")
    result = parse(filename)
    observations = sorted(result.observations, key=lambda item: item.date)
    last_days = arguments.lastDays()
    date_range = brondata.getDateRange(metenisweten)
    if last_days > 0:
        date_range = date_range[-last_days:]

    from datetime import date
    observations = [
        item for item in observations
        if date_range[0].date() <= date.fromisoformat(item.date) <= date_range[-1].date()
    ]
    dates = [date.fromisoformat(item.date) for item in observations]
    values = [item.value for item in observations]
    ymax = nice_maximum(max(values) * 1.08)

    fig, ax = plt.subplots(figsize=(10, 5))
    # Match the plot area used by the existing dashboard graphs so stacked
    # axes and grid lines have the same visual width.
    fig.subplots_adjust(top=0.92, bottom=0.16, left=0.09, right=0.91)
    ax.plot(dates, values, color="darkorange", linewidth=2,
            label=f"IC-opnames per week (laatste: {int(values[-1])})")
    ax.fill_between(dates, values, color="orange", alpha=0.18)
    ax.grid(which="both", axis="both", linestyle="-.", color="gray", linewidth=1, alpha=0.3)
    ax.set_ylim(0, ymax)
    ax.set_xlim(date_range[0], date_range[-1])
    ax.set_ylabel("Aantal nieuwe IC-opnames per week")
    ax.set_xlabel("Datum")
    ax.set_title("Ernstige luchtweginfecties op de IC in Nederland")
    ax.legend(loc="upper left")

    generated = build_datetime().strftime("%Y-%m-%d %H:%M")
    fig.text(0.01, 0.025, f"Gegenereerd op {generated}, data t/m week van {dates[-1]}.\nSource code: http://github.com/realrolfje/coronadata",
             ha="left", fontsize=8, color="gray")
    fig.text(0.99, 0.025, "Dekking varieert; recente weken kunnen worden herzien.\nBron: RIVM/NICE SARI-surveillance",
             ha="right", fontsize=8, color="gray")

    suffix = f"-{last_days}" if last_days > 0 else ""
    plt.savefig(GRAPHS_DIR / f"sari{suffix}.svg", format="svg")
    plt.close(fig)


if __name__ == "__main__":
    createSariGraph(brondata.readjson(DAILY_STATS))
    sys.exit(0)
