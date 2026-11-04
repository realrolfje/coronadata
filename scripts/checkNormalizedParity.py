#!/usr/bin/env python3

import hashlib
import json
from pathlib import Path
import sqlite3

from pipeline.legacy_daily_stats import parse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT_ROOT / "data" / "daily-stats.json"
DATABASE = PROJECT_ROOT / "cache" / "normalized-v1.sqlite"


def digest(rows):
    canonical = json.dumps(rows, separators=(",", ":"), sort_keys=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


def main():
    expected = parse(SOURCE)
    expected_by_metric = {}
    for observation in expected.observations:
        expected_by_metric.setdefault(observation.metric, []).append(
            [observation.date, observation.value, observation.source_id,
             json.dumps(observation.dimensions, sort_keys=True, separators=(",", ":"))]
        )
    for rows in expected_by_metric.values():
        rows.sort()

    connection = sqlite3.connect(DATABASE)
    actual_by_metric = {}
    for metric in expected_by_metric:
        actual_by_metric[metric] = [list(row) for row in connection.execute(
            """
            SELECT observation_date, value, source_id, dimensions_json
            FROM observations WHERE metric = ?
            ORDER BY observation_date, value, source_id, dimensions_json
            """, (metric,)
        )]
    connection.close()

    metrics = {}
    all_match = True
    for metric, expected_rows in sorted(expected_by_metric.items()):
        actual_rows = actual_by_metric[metric]
        matches = expected_rows == actual_rows
        all_match = all_match and matches
        metrics[metric] = {
            "matches": matches,
            "legacy_count": len(expected_rows),
            "normalized_count": len(actual_rows),
            "legacy_sha256": digest(expected_rows),
            "normalized_sha256": digest(actual_rows),
        }

    report = {
        "schema_version": 1,
        "all_metrics_match": all_match,
        "metric_count": len(metrics),
        "metrics": metrics,
        "intentional_differences": [
            "Null legacy fields are omitted rather than stored as observations.",
            "Legacy date strings and display metadata are not observations.",
            "Nested age groups and variants become dimensions instead of dynamic columns.",
        ],
    }
    report_path = PROJECT_ROOT / "data" / "normalized-v1-parity.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"Normalized parity: {'passed' if all_match else 'failed'} ({len(metrics)} metrics)")
    return 0 if all_match else 1


if __name__ == "__main__":
    raise SystemExit(main())
