#!/usr/bin/env python3

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import tempfile

from pipeline.legacy_daily_stats import TRANSFORMER_VERSION, parse
from pipeline.storage import SQLiteObservationStore


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main():
    argument_parser = argparse.ArgumentParser(
        description="Rebuild normalized schema v1 from the preserved compatibility dataset."
    )
    argument_parser.add_argument(
        "--source", type=Path, default=PROJECT_ROOT / "data" / "daily-stats.json"
    )
    argument_parser.add_argument(
        "--database", type=Path, default=PROJECT_ROOT / "cache" / "normalized-v1.sqlite"
    )
    arguments = argument_parser.parse_args()
    result = parse(arguments.source)

    arguments.database.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix="normalized-v1-", suffix=".sqlite", dir=arguments.database.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        with SQLiteObservationStore(temporary) as store:
            inserted = store.write(result)
        os.replace(temporary, arguments.database)
    finally:
        temporary.unlink(missing_ok=True)

    statuses = Counter(observation.status for observation in result.observations)
    sources = Counter(observation.source_id for observation in result.observations)
    metrics = Counter(observation.metric for observation in result.observations)
    manifest = {
        "schema_version": 1,
        "transformer": "legacy_daily_stats",
        "transformer_version": TRANSFORMER_VERSION,
        "source_file": "data/daily-stats.json",
        "source_sha256": result.provenance["sha256"],
        "newest_observation": result.newest_observation,
        "observation_count": len(result.observations),
        "inserted_observation_count": inserted,
        "statuses": dict(sorted(statuses.items())),
        "sources": dict(sorted(sources.items())),
        "metrics": dict(sorted(metrics.items())),
        "database": "cache/normalized-v1.sqlite (rebuildable, not tracked)",
    }
    manifest_path = PROJECT_ROOT / "data" / "normalized-v1-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
