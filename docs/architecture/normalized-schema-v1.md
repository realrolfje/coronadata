# Normalized observation schema v1

Status: implemented in parallel; graph consumers still use `data/daily-stats.json`.

Each row in the rebuildable SQLite `observations` table represents one numeric observation:

| Field | Meaning |
|---|---|
| `schema_version` | Integer schema version; currently `1` |
| `observation_date` | ISO `YYYY-MM-DD` date to which the value applies |
| `metric` | Stable snake-case metric identifier |
| `value` | Numeric value; a missing legacy value creates no row |
| `unit` | Stable unit such as `persons`, `percent`, `ratio`, or `sequenced_samples` |
| `geography` | Geography identifier; `NL` unless a source supplies a more specific area |
| `source_id` | Stable registry ID, or `derived_coronadata` for project calculations |
| `publication_date` | Source publication date when known |
| `status` | `reported`, `revised`, `imputed`, or `calculated` |
| `dimensions_json` | Metric-specific dimensions, such as variant or age group |
| `provenance_json` | Raw checksum/path and transformer name/version |

## Status and null rules

- `reported` is a value stated by a source, including a source-published estimate.
- `revised` is reserved for a source revision that supersedes an earlier value. Schema v1 can
  represent it, but the legacy conversion has no reliable revision history and creates none.
- `imputed` is a deliberately filled value. Schema v1 creates none: gaps remain gaps.
- `calculated` is produced from one or more observations by this project.
- `null` means no observation and is omitted. Numeric zero remains a stored value.

## Date semantics

The observation date is the date represented by the legacy daily record or active source record,
not the download date. Source publication dates are stored separately when available. Weekly
variant observations use the source's week-start date.

## Compatibility and rebuilding

Run:

```shell
.venv/bin/python scripts/buildNormalizedData.py
.venv/bin/python scripts/checkNormalizedParity.py
```

This rebuilds ignored `cache/normalized-v1.sqlite` from the unchanged compatibility file and writes
tracked manifest and parity reports under `data/`. Graphs continue reading `daily-stats.json` until
an explicit later migration switches them.
