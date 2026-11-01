#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
import sys

from pipeline.download import fetch_json_source
from pipeline.infectieradar_ari import parse as parse_ari
from pipeline.variants import parse as parse_variants
from pipeline.wastewater import parse as parse_wastewater
from pipeline.storage import SQLiteObservationStore


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PARSERS = {
    "rivm_wastewater": parse_wastewater,
    "rivm_variants": parse_variants,
    "rivm_infectieradar_ari": parse_ari,
}
MINIMUM_BYTES = {
    "rivm_wastewater": 1_000_000,
    "rivm_variants": 100_000,
    "rivm_infectieradar_ari": 10_000,
}


def update_source(source, snapshot_root):
    return fetch_json_source(
        source_id=source["id"],
        url=source["url"],
        target=PROJECT_ROOT / source["cache_path"],
        snapshot_root=snapshot_root,
        parser=PARSERS[source["id"]],
        minimum_bytes=MINIMUM_BYTES[source["id"]],
    )


def main():
    argument_parser = argparse.ArgumentParser(
        description="Download and validate active epidemiological sources."
    )
    argument_parser.add_argument(
        "source_ids", nargs="*", metavar="SOURCE_ID",
        help="Update selected sources; defaults to all configured active sources.",
    )
    arguments = argument_parser.parse_args()
    unknown = set(arguments.source_ids) - PARSERS.keys()
    if unknown:
        argument_parser.error(f"unknown source ID(s): {', '.join(sorted(unknown))}")
    registry = json.loads((PROJECT_ROOT / "sources.json").read_text())
    wanted = set(arguments.source_ids or PARSERS)
    snapshot_root = PROJECT_ROOT / "cache" / "raw"
    failures = []

    with SQLiteObservationStore(PROJECT_ROOT / "cache" / "observations.sqlite") as store:
        for source in registry["sources"]:
            if source["id"] not in wanted:
                continue
            try:
                result = update_source(source, snapshot_root)
                inserted = store.write(result.parser_result)
                state = "updated" if result.changed else "unchanged"
                print(
                    f"{source['id']}: {state}; {result.byte_count} bytes; "
                    f"publication {result.parser_result.publication_date}; "
                    f"newest observation {result.parser_result.newest_observation}; "
                    f"normalized inserts {inserted}; snapshot {result.snapshot}"
                )
                for warning in result.parser_result.warnings:
                    print(f"{source['id']}: warning: {warning}")
            except Exception as error:
                failures.append(f"{source['id']}: {error}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
