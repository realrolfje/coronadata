#!/usr/bin/env python3
"""Compatibility wrapper for the separated Coronadata estimate calculation."""

from pipeline.calculations import calculate_coronadata_estimate

from .datecache import dateCache
from .metenisweten import metenisweten, writeMetenIsWeten


def calculate():
    report = calculate_coronadata_estimate(metenisweten)
    print(f"Calculated {report.observations_written} Coronadata estimates.")
    return report


if __name__ == "__main__":
    calculate()
    writeMetenIsWeten()
    dateCache.cacheReport()
