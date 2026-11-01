#!/usr/bin/env python3
"""Compatibility facade for legacy graph code.

Pipeline orchestration lives in :mod:`pipeline.stages`. This module retains only the formatting,
date, and compatibility helpers imported by existing graph modules.
"""

import datetime
import json

from pipeline.calculations import smooth as _smooth
from pipeline.stages import cache_is_recent, run_update_pipeline

from .datecache import dateCache
from .utilities import (
    decimalstring,
    isnewer,
    logError,
    readjson,
    sortDictOnKey,
    switchdecimals,
    writejson,
)


def smooth(values):
    return _smooth(values, iterations=2, window=13, order=1)


def double_savgol(values, iterations, window, order):
    return _smooth(values, iterations=iterations, window=window, order=order)


def intOrNone(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def intOrZero(value):
    return intOrNone(value) or 0


def freshdata():
    """Compatibility entry point for individually executed legacy graph scripts."""
    report = run_update_pipeline()
    return report.persisted or cache_is_recent()


def getDateRange(daily):
    dates = [dateCache.parse(date) for date in daily]
    minimum = max(min(dates), dateCache.parse("2020-03-01"))
    maximum = max(dates)
    print(maximum)
    return [
        minimum + datetime.timedelta(days=offset)
        for offset in range((maximum - minimum).days + 7)
    ]


def printDict(value):
    print(json.dumps(value, indent=4))


if __name__ == "__main__":
    freshdata()
