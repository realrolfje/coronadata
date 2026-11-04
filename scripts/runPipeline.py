#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

from pipeline.stages import run_update_pipeline


def main():
    parser = argparse.ArgumentParser(description="Run explicit Coronadata pipeline stages.")
    parser.add_argument("command", choices=("update",), help="Pipeline operation to run.")
    parser.add_argument("--force", action="store_true", help="Replay transforms even when inputs are unchanged.")
    parser.add_argument("--report", type=Path, help="Also write the summary as JSON to this file.")
    parser.add_argument("source_ids", nargs="*", metavar="SOURCE_ID")
    arguments = parser.parse_args()

    report = run_update_pipeline(
        source_ids=arguments.source_ids or None, force=arguments.force
    )
    summary = {
        "downloads": {
            item.source_id: {
                "changed": item.changed,
                "publication_date": item.parser_result.publication_date,
                "newest_observation": item.parser_result.newest_observation,
            }
            for item in report.downloads
        },
        "active_transforms": report.active_transforms,
        "preserved_transforms": [item.name for item in report.transformations],
        "calculations": [item.name for item in report.calculations],
        "persisted": report.persisted,
        "changed": report.changed,
    }
    print(json.dumps(summary, indent=2))
    if arguments.report:
        arguments.report.write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
