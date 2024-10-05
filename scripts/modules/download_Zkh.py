#!/usr/bin/env python3
#
# Downloads the NICE dataset containing intensive care and hospitak intake.
#
# Please note that these files are no longer in this location (gave 404) since beginning of 2024
#

import os
from utilities import downloadIfStale, readjson
from defaults import cachedir
from metenisweten import initrecord
from datecache import dateCache


def download_intake_cumulative(force=False) -> str:
    filename = os.path.join(cachedir, "NICE-intake-cumulative.json")
    if downloadIfStale(
        filename=filename,
        url="https://www.stichting-nice.nl/covid-19/public/intake-cumulative/",
        force = force):
        return filename
    else:
        return None


def download_intake_count(force=False) -> str:
    filename = os.path.join(cachedir, "NICE-intake-count.json")
    if downloadIfStale(
        filename=filename,
        url="https://www.stichting-nice.nl/covid-19/public/intake-count/",
        force = force):
        return filename
    else:
        return None


def download_zkh_intake_count(force=False) -> str:
    filename = os.path.join(cachedir, "NICE-zkh-intake-count.json")
    if downloadIfStale(
        filename=filename,
        url="https://www.stichting-nice.nl//covid-19/public/zkh/intake-count/",
        force = force):
        return filename
    else:
        return None


def store_intake_count(filename) -> bool:
    if filename == None:
        return False
    print("Add intensive care data")
    for record in readjson(filename):
        if dateCache.isvaliddate(record['date'], filename):
            initrecord(record['date'])['nu_op_ic'] = record['value']
    return True


def store_intake_cumulative(filename) -> bool:
    if filename == None:
        return False
    for record in readjson(filename):
        if dateCache.isvaliddate(record['date'], filename):
            initrecord(record['date'])['geweest_op_ic'] += record['value']
    return True


def store_zkh_intake_count(filename) -> bool:
    if filename == None:
        return False
    for record in readjson(filename):
        if not dateCache.isvaliddate(record['date'], filename):
            initrecord(record['date'])['nu_opgenomen'] = record['value']
    return True


def process(force=False) -> bool:
    """Download and process the data"""
    new = [
        store_intake_count(download_intake_count(force)),
        store_intake_cumulative(download_intake_cumulative(force)),
        store_zkh_intake_count(download_zkh_intake_count(force))
    ]
    return any(new)

if __name__ == "__main__":
    process(force=True)
    dateCache.cacheReport()
