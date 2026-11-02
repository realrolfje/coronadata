#!/usr/bin/env python3
"""Validate that every cached RIVM variant week is mutually exclusive."""

import argparse
import hashlib
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from modules.defaults import CACHE_DIR, DATA_DIR, VARIANT_TAXONOMY
from pipeline.variant_taxonomy import load_taxonomy, make_exclusive_week


def validate(source_path, taxonomy_path):
    raw = source_path.read_bytes()
    records = json.loads(raw)
    taxonomy = load_taxonomy(taxonomy_path)
    weeks = {}
    for record in records:
        weeks.setdefault(record["Date_of_statistics_week_start"], []).append(record)
    dates = sorted(weeks)

    summaries = []
    unresolved = []
    invalid_weeks = []
    for date, week_records in sorted(weeks.items()):
        try:
            result = make_exclusive_week(week_records, taxonomy)
        except ValueError as error:
            invalid_weeks.append({"date": date, "error": str(error)})
            continue
        week_unresolved = [
            {"date": date, "relation": relation}
            for relation in result.unresolved_parents
        ]
        unresolved.extend(week_unresolved)
        if week_unresolved:
            invalid_weeks.append({
                "date": date,
                "error": "onopgeloste ouderrelatie(s): "
                + ", ".join(item["relation"] for item in week_unresolved),
            })
            continue
        summaries.append({
            "date": date,
            "sample_size": result.sample_size,
            "exclusive_total": result.total,
            "unassigned": result.sample_size - result.total,
        })

    try:
        source_name = str(source_path.relative_to(PROJECT_ROOT))
    except ValueError:
        source_name = str(source_path)

    return {
        "schema_version": 1,
        "taxonomy_version": taxonomy.version,
        "source": {
            "path": source_name,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "record_count": len(records),
        },
        "week_count": len(weeks),
        "valid_week_count": len(summaries),
        "first_week": dates[0],
        "last_week": dates[-1],
        "unresolved_relations": unresolved,
        "invalid_weeks": invalid_weeks,
        "weeks": summaries,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", type=Path, default=CACHE_DIR / "COVID-19_varianten.json"
    )
    parser.add_argument("--taxonomy", type=Path, default=VARIANT_TAXONOMY)
    parser.add_argument(
        "--output", type=Path, default=DATA_DIR / "variant-taxonomy-validation.json"
    )
    args = parser.parse_args()

    report = validate(args.source, args.taxonomy)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"Variantentaxonomie gecontroleerd voor {report['week_count']} weken "
        f"({report['first_week']} t/m {report['last_week']}); "
        f"rapport: {args.output}"
    )
    for invalid in report["invalid_weeks"]:
        print(
            f"WAARSCHUWING: variantenweek {invalid['date']} overgeslagen: "
            f"{invalid['error']}"
        )


if __name__ == "__main__":
    main()
