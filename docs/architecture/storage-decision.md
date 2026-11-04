# Intermediate storage decision

Date: 2026-11-01
Status: accepted for incremental migration

## Decision

Use SQLite as the intermediate observation store for newly migrated source adapters. Keep raw
downloads as immutable files and keep `data/daily-stats.json` unchanged as the preserved historical
baseline until a later migration has demonstrated parity.

Parsers return a storage-independent `ParserResult` containing normalized observations,
provenance, source dates, and warnings. They do not issue SQL directly. An `ObservationStore`
interface allows the same parser result to be tested in memory and written to SQLite.

## Pilot evidence

The wastewater pilot:

- parses the preserved RIVM wastewater JSON through a source-specific adapter;
- writes treatment-plant observations into a typed SQLite table;
- runs the daily-average query needed by the existing RNA graph;
- compares that query with the in-memory implementation;
- verifies that importing the same raw snapshot twice adds no observations; and
- records the raw-file checksum and source dates in the import metadata.

Run it with:

```shell
.venv/bin/python scripts/pilotWastewaterSqlite.py
```

The generated pilot database and report live in ignored `cache/` files. They can be deleted and
rebuilt from the raw source file.

## Consequences

- Cross-source calculations can use SQL joins and views without coupling parsers to calculations.
- SQLite is a rebuildable processing artifact, not the sole historical archive.
- The current graph code continues to use `daily-stats.json` until parity tests exist.
- Revisions to an already imported source observation require an explicit revision policy; the
  pilot currently favors idempotency and ignores an identical key on re-import.
