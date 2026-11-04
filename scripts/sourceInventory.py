#!/usr/bin/env python3

import argparse
import datetime
import json
from pathlib import Path
import sys

from pipeline.registry import inspect_registry, load_registry, markdown_report


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description="Inspect registered Coronadata sources.")
    parser.add_argument(
        "--today",
        type=datetime.date.fromisoformat,
        help="Override today's date for deterministic tests (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--fail-required",
        action="store_true",
        help="Return a failure status when a required source is unhealthy.",
    )
    arguments = parser.parse_args()

    registry = load_registry(PROJECT_ROOT / "sources.json")
    report = inspect_registry(PROJECT_ROOT, registry, today=arguments.today)

    json_path = PROJECT_ROOT / "cache" / "source-health.json"
    markdown_path = PROJECT_ROOT / "SOURCE_STATUS.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n")
    markdown_path.write_text(markdown_report(report))

    print(f"Source health: {report['status']}")
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {markdown_path}")
    return 1 if arguments.fail_required and report["status"] == "blocked" else 0


if __name__ == "__main__":
    sys.exit(main())
