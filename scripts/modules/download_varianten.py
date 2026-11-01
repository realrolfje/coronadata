#!/usr/bin/env python3

# Downloads the varianten dataset.
# See data.rivm.nl, Covid-19 reproductiegetal
# See https://data.rivm.nl/covid-19/
#
#
import os
from .utilities import readjson
from .defaults import cachedir
from .metenisweten import initrecord
from .datecache import dateCache
from pathlib import Path
from pipeline.download import fetch_json_source
from pipeline.variants import parse as parse_variants


PRESERVED_HISTORY_END = "2024-09-23"


def download(force=False) -> str:
    filename = os.path.join(cachedir, "COVID-19_varianten.json")
    result = fetch_json_source(
        source_id="rivm_variants",
        url='https://data.rivm.nl/covid-19/COVID-19_varianten.json',
        target=Path(filename),
        snapshot_root=Path(cachedir) / "raw",
        parser=parse_variants,
        minimum_bytes=100_000,
    )
    baseline = Path(cachedir).parent / "data" / "daily-stats.json"
    if result.changed or force or not baseline.exists() or Path(filename).stat().st_mtime > baseline.stat().st_mtime:
        return filename
    return None


def store(downloaded_file) -> bool:
    if downloaded_file == None:
        return False 

    data = readjson(downloaded_file)
    initialized_dates = set()
    for record in data:
        datum = record['Date_of_statistics_week_start']
        if datum <= PRESERVED_HISTORY_END:
            continue
        m = initrecord(datum)
        if datum not in initialized_dates:
            m['varianten'] = {}
            initialized_dates.add(datum)
        if record['Variant_code'] not in m['varianten']:
            m['varianten'][record['Variant_code']] = {
                'name': record['Variant_name'],
                'ECDC_category': record['ECDC_category'],
                'WHO_category': record['WHO_category'],
                'includes_old_samples': record.get('May_include_samples_listed_before', False),
                'sample_size': record['Sample_size'],
                'cases': record['Variant_cases']
            }
        # if datum.startswith('2024'):
        #     print(f"{datum} {m['varianten'][record['Variant_code']]} {m['varianten'][record['Variant_code']]['sample_size']} {m['varianten'][record['Variant_code']]['cases']}")
    return True


def process(force=False):
    """Download and process the data"""
    store(download(force))

if __name__ == "__main__":
    process(force=True)
    dateCache.cacheReport()
