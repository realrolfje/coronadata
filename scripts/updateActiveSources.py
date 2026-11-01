#!/usr/bin/env python3

import argparse
from pathlib import Path
import sys

from pipeline.active_sources import ADAPTERS, download_source
from pipeline.storage import SQLiteObservationStore


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main():
    argument_parser = argparse.ArgumentParser(
        description="Download and validate active epidemiological sources."
    )
    argument_parser.add_argument(
        "source_ids", nargs="*", metavar="SOURCE_ID",
        help="Update selected sources; defaults to all configured active sources.",
    )
    arguments = argument_parser.parse_args()
    unknown = set(arguments.source_ids) - ADAPTERS.keys()
    if unknown:
        argument_parser.error(f"unknown source ID(s): {', '.join(sorted(unknown))}")
    wanted = list(arguments.source_ids or ADAPTERS)
    failures = []

    with SQLiteObservationStore(PROJECT_ROOT / "cache" / "observations.sqlite") as store:
        for source_id in wanted:
            try:
                result = download_source(PROJECT_ROOT, source_id)
                inserted = store.write(result.parser_result)
                state = "updated" if result.changed else "unchanged"
                print(
                    f"{source_id}: {state}; {result.byte_count} bytes; "
                    f"publication {result.parser_result.publication_date}; "
                    f"newest observation {result.parser_result.newest_observation}; "
                    f"normalized inserts {inserted}; snapshot {result.snapshot}"
                )
                for warning in result.parser_result.warnings:
                    print(f"{source_id}: warning: {warning}")
            except Exception as error:
                failures.append(f"{source_id}: {error}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
