#!/usr/bin/env python3
#
#

import pytz
from pathlib import Path

timezone = pytz.timezone("Europe/Amsterdam")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = PROJECT_ROOT / "cache"
DOCS_DIR = PROJECT_ROOT / "docs"
GRAPHS_DIR = DOCS_DIR / "graphs"
TEMPLATES_DIR = DOCS_DIR / "templates"
DAILY_STATS = DATA_DIR / "daily-stats.json"

# Compatibility aliases for modules not migrated to pathlib yet.
datadir = str(DATA_DIR)
cachedir = str(CACHE_DIR)

if __name__ == "__main__":
    print(f"Default timezone is {timezone}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Default directory for storing/saving/committing downloaded files: {DATA_DIR}")
    print(f"Default directory for caching files: {CACHE_DIR}")
