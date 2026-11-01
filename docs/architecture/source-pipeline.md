# Source pipeline

New and migrated sources follow this boundary:

```text
sources.json -> downloader/raw snapshot -> source parser -> ParserResult
                                                       -> ObservationStore
                                                       -> calculations -> graphs
```

- `sources.json` describes ownership, lifecycle, freshness, schema and consumers.
- A downloader will validate the HTTP response and preserve changed raw input in Phase 3.
- Each unrelated source format gets its own parser. Parsers emit `ParserResult` and contain no
  graphing or cross-source calculations.
- `ObservationStore` keeps parsers independent of SQLite. The memory implementation supports fast
  tests; SQLite is the selected rebuildable intermediate store.
- Existing `data/daily-stats.json` remains the immutable historical compatibility baseline until
  later parity tests justify switching a consumer.

The wastewater adapter is the first implementation of this design. Legacy imports still embedded
in `scripts/modules/brondata.py` will be migrated one source at a time while repairing active
sources, rather than being rewritten all at once.
