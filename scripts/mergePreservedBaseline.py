#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Restore preserved historical records and retain only later generated records."
    )
    parser.add_argument("baseline", type=Path)
    parser.add_argument("current", type=Path)
    arguments = parser.parse_args()

    baseline = json.loads(arguments.baseline.read_text())
    current = json.loads(arguments.current.read_text())
    cutoff = max(baseline)
    merged = dict(baseline)
    merged.update({date: record for date, record in current.items() if date > cutoff})
    arguments.current.write_text(json.dumps(dict(sorted(merged.items()))))
    print(
        f"Restored {len(baseline)} preserved records through {cutoff}; "
        f"kept {len(merged) - len(baseline)} later records."
    )


if __name__ == "__main__":
    main()
