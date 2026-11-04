#!/usr/bin/env python3

import argparse
import json
import math
from pathlib import Path
import sys

from pipeline.storage import MemoryObservationStore, SQLiteObservationStore
from pipeline.wastewater import METRIC, SOURCE_ID, parse


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def averages_match(left, right):
    if len(left) != len(right):
        return False
    return all(
        left_date == right_date
        and math.isclose(left_value, right_value, rel_tol=1e-12, abs_tol=0.001)
        for (left_date, left_value), (right_date, right_value) in zip(left, right)
    )


def main():
    parser = argparse.ArgumentParser(description="Run the wastewater SQLite storage pilot.")
    parser.add_argument(
        "--source",
        type=Path,
        default=PROJECT_ROOT / "cache" / "COVID-19_rioolwaterdata.json",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=PROJECT_ROOT / "cache" / "wastewater-pilot.sqlite",
    )
    arguments = parser.parse_args()

    result = parse(arguments.source)
    memory = MemoryObservationStore()
    memory.write(result)
    memory_averages = memory.daily_average(SOURCE_ID, METRIC)

    arguments.database.parent.mkdir(parents=True, exist_ok=True)
    with SQLiteObservationStore(arguments.database) as sqlite_store:
        sqlite_store.write(result)
        second_write_changes = sqlite_store.write(result)
        sqlite_averages = sqlite_store.daily_average(SOURCE_ID, METRIC)

    if second_write_changes != 0:
        raise RuntimeError("re-importing the same raw source changed the SQLite store")
    if not averages_match(memory_averages, sqlite_averages):
        raise RuntimeError("memory and SQLite daily-average queries differ")

    report = {
        "source_id": result.source_id,
        "raw_sha256": result.provenance["sha256"],
        "raw_record_count": result.provenance["record_count"],
        "observation_count": len(result.observations),
        "publication_date": result.publication_date,
        "newest_observation": result.newest_observation,
        "daily_average_count": len(sqlite_averages),
        "latest_daily_average": sqlite_averages[-1] if sqlite_averages else None,
        "idempotent_reimport": True,
        "memory_sqlite_match": True,
        "database": str(arguments.database),
    }
    report_path = PROJECT_ROOT / "cache" / "wastewater-pilot-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
