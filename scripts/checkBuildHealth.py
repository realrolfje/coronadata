#!/usr/bin/env python3

import argparse
import datetime
import json
from pathlib import Path
import sys

from pipeline.registry import inspect_registry, load_registry


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ERRORS_FILE = PROJECT_ROOT / "cache" / "errors.log"
REPORT_FILE = PROJECT_ROOT / "cache" / "build-report.json"

RETIRED_SOURCE_URLS = (
    "https://www.stichting-nice.nl/covid-19/public/",
    "https://www.stichting-nice.nl//covid-19/public/",
)
BLOCKING_PREFIXES = (
    "Problem opening",
    "No data received",
)


def classify(lines):
    blocking = []
    warnings = []
    for line in lines:
        if line.startswith(BLOCKING_PREFIXES) and not any(
            url in line for url in RETIRED_SOURCE_URLS
        ):
            blocking.append(line)
        else:
            warnings.append(line)
    return blocking, warnings


def main():
    parser = argparse.ArgumentParser(
        description="Create a build-health report and fail on blocking source errors."
    )
    parser.parse_args()

    lines = []
    if ERRORS_FILE.exists():
        lines = list(
            dict.fromkeys(
                line.strip()
                for line in ERRORS_FILE.read_text().splitlines()
                if line.strip()
            )
        )

    blocking, warnings = classify(lines)
    registry = load_registry(PROJECT_ROOT / "sources.json")
    source_report = inspect_registry(PROJECT_ROOT, registry)
    (PROJECT_ROOT / "cache" / "source-health.json").write_text(
        json.dumps(source_report, indent=2) + "\n"
    )
    for source in source_report["sources"]:
        if source["blocking"]:
            blocking.append(
                f"Source {source['id']} is {source['health']}: "
                + " ".join(source["messages"])
            )
    report = {
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "blocked" if blocking else "healthy",
        "blocking_errors": blocking,
        "warnings": warnings,
        "source_health": source_report["status"],
    }
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(json.dumps(report, indent=2) + "\n")

    print(f"Build health: {report['status']}")
    print(f"Warnings: {len(warnings)}; blocking errors: {len(blocking)}")
    print(f"Report: {REPORT_FILE}")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
