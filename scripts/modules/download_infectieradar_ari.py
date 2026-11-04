#!/usr/bin/env python3

import os
from pathlib import Path

from .defaults import cachedir
from .metenisweten import initrecord
from pipeline.download import fetch_json_source
from pipeline.infectieradar_ari import parse


URL = "https://data.rivm.nl/covid-19/ARI_Infectieradar_symptomen_per_dag.json"


def download(force=False):
    filename = Path(cachedir) / "ARI_Infectieradar_symptomen_per_dag.json"
    result = fetch_json_source(
        source_id="rivm_infectieradar_ari",
        url=URL,
        target=filename,
        snapshot_root=Path(cachedir) / "raw",
        parser=parse,
        minimum_bytes=10_000,
    )
    baseline = Path(cachedir).parent / "data" / "daily-stats.json"
    cache_is_newer = (
        not baseline.exists() or filename.stat().st_mtime > baseline.stat().st_mtime
    )
    return filename if result.changed or force or cache_is_newer else None


def store(filename):
    if filename is None:
        return False
    result = parse(filename)
    for observation in result.observations:
        initrecord(observation.date)["rivm_infectieradar_ari_perc"] = observation.value
    print(
        "Newest ARI Infectieradar data: "
        f"{result.newest_observation} (published {result.publication_date})"
    )
    return True


def process(force=False):
    return store(download(force))
