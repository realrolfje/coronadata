# Coronadata restoration and modernization plan

Status: active
Created: 2026-11-01  
Purpose: preserve the historical COVID-19 dataset, restore the parts of the pipeline that can still be updated, and make the project maintainable without silently changing historical results.

## Goals

- Preserve the original downloaded and derived data.
- Make the historical site reproducible without depending on retired services.
- Identify which sources are active, frozen, retired, or broken.
- Update indicators for which an authoritative and compatible source still exists.
- Clearly mark series that have legitimately ended.
- Refactor the code only after its current behavior is protected by tests.
- Publish only meaningful, validated updates.

## Non-goals

- Do not manufacture continuity by joining datasets with incompatible definitions.
- Do not rewrite historical observations merely because a source changed its schema.
- Do not delete old data after migrating to a new representation.
- Do not perform a broad rewrite before an offline baseline can be reproduced.
- Do not treat an HTTP success response as proof that a dataset is current or valid.

## Working principles

1. Preserve first, repair second, refactor third.
2. Raw source data is immutable once archived.
3. Every normalized value should have source and transformation provenance.
4. Active, frozen, retired, and broken sources are different states and should be handled differently.
5. Historical and current surveillance can coexist without pretending they are the same series.
6. Generated files are outputs, not the source of truth.
7. Each phase should leave the project in a usable state.

## Current situation

- `cache/` contains about 3.3 GB of ignored raw or cached source data.
- `data/` contains about 128 MB of tracked data, including `data/daily-stats.json` and dated snapshots.
- The pipeline combines downloads, transformations, calculations, graph generation, page generation, Git operations, and publishing.
- The currently logged hard failures are the three removed Stichting NICE JSON endpoints.
- Several other sources return old but valid files and can therefore appear healthy while no longer updating.
- `update.sh` currently pulls, builds, appends a timestamp, commits everything, and pushes even when no epidemiological source changed.

## Source inventory

This table is backed by `sources.json` and the generated `SOURCE_STATUS.md`. Compatibility with a
replacement must still be confirmed before changing a historical series.

| Source or metric | Current endpoint/module | Initial status | Proposed treatment | Verified |
|---|---|---|---|---|
| RIVM wastewater measurements | `download_rioolwaterdata.py` | Active | Keep; evaluate the national aggregate feed where appropriate | [x] |
| RIVM variants | `download_varianten.py` | Active | Keep; add schema and freshness validation | [x] |
| Infectieradar symptoms | Old `COVID-19_Infectieradar...` URL in `brondata.py` | Frozen | Research migration to active `ARI_Infectieradar...`; keep old history unchanged | [x] |
| RIVM reproduction number | `download_Rt.py` | Frozen | Preserve and show an explicit end date | [x] |
| RIVM national cases | `download_casus_landelijk.py` | Frozen or retired | Preserve and show an explicit end date | [x] |
| RIVM tests | `brondata.py` and CoronaWatchNL | Frozen | Preserve; do not imply current testing coverage | [x] |
| RIVM prevalence estimate | `brondata.py` | Frozen | Preserve and label as historical estimate | [x] |
| RIVM vaccination coverage | `brondata.py` | Frozen | Preserve and show an explicit end date | [x] |
| LCPS hospital and IC data | `download_lcps_ziekenhuisopnames.py` and `brondata.py` | Ended in 2024 | Preserve final series; investigate only definition-compatible successors | [x] |
| Stichting NICE hospital and IC data | `download_Zkh.py` | Endpoints removed | Stop live requests; retain cached historical data | [x] |
| Government dashboard JSON | `brondata.py` | Unknown | Verify endpoint, schema, freshness, and whether it is still used | [x] |
| Apple mobility | `brondata.py` | Frozen in 2022 | Treat as a completed historical series | [x] |
| ECDC map | Disabled in `brondata.py` | Retired | Remove from active pipeline; retain historical artifact | [x] |
| CoronaWatchNL test data | `brondata.py` | Unknown/frozen | Verify repository status and keep only if historically necessary | [x] |
| Page-hit counter | `updatePageHits.py` | Non-epidemiological | Separate from the data pipeline | [x] |

Useful official references:

- [RIVM COVID-19 datasets](https://data.rivm.nl/covid-19/)
- [LCPS datafeed](https://lcps.nu/datafeed/)
- [Stichting NICE](https://www.stichting-nice.nl/)

## Phase 1: preserve and establish a baseline

### 1.1 Archive the current data

Keep this deliberately simple. The archive is a manual safety copy, not a new storage system.

- [x] Stop the update process while creating the archive so files cannot change halfway through.
- [x] Create a dated ZIP archive containing `cache/` and `data/`, for example `coronadata-data-2026-11-01.zip`.
- [x] Store the ZIP outside the Git repository directory.
- [x] Test the completed archive with `unzip -t`.
- [x] Create a SHA-256 checksum file next to the ZIP.
- [x] Record the archive filename, checksum, creation date, and restore command in this document.

Restore procedure:

```shell
cd /path/to/coronadata
unzip /path/outside/repository/coronadata-data-YYYY-MM-DD.zip
```

Archive record (complete this after creating it):

| Field | Value |
|---|---|
| Archive | `/Users/rolf/github/coronadata-data-2026-11-01.zip` (101 MB) |
| Created | 2026-11-01 |
| SHA-256 | `6dbe5218e6aeb84e7228b8507b1461f050a19a51e8b534c402bab5d52feb91a4` |
| Contents | `cache/`, `data/` |

### 1.2 Establish an offline reference build

Treat the tracked `data/daily-stats.json` as the complete historical baseline. The cache on this
laptop may not contain every original source file because the production importer ran on another
server. Re-importing all historical source data is therefore not a requirement for the reference
build and must not overwrite the baseline.

- [x] Add a render-only command that skips downloads, source processing, calculations, and writes to `data/daily-stats.json`.
- [x] Generate the graphs and pages from the existing `data/daily-stats.json` and other preserved inputs required only for rendering.
- [x] Identify any graph that still depends on cache data not represented in `daily-stats.json`, and either preserve that input or move the required metadata into a tracked render fixture. The 365-day age heatmap and test graph currently retain their existing output when their historical source window is unavailable.
- [x] Record representative numerical graph inputs and date ranges as the primary regression baseline.
- [x] Compare rendered graph output where it is deterministic; otherwise compare the data supplied to the renderer. The baseline fixture verifies the processed-data digest, graph date range, and latest observations for representative series.
- [x] Add regression tests for important historical totals, known dates, and series end dates.
- [x] Make the render-only baseline leave `data/daily-stats.json` unchanged; verification uses its SHA-256 checksum.
- [x] Document that full historical source re-import is not reproducible unless the original server cache is recovered.

### 1.3 Make publishing safe

- [x] Stop timestamp-only changes from producing commits.
- [x] Do not publish when an active source fails validation. Required active sources now undergo schema and content-freshness validation through the registry health check.
- [x] Replace `git pull -X theirs` with an explicit synchronization step, preferably `git pull --ff-only`, that stops when local and remote history have diverged. `-X theirs` can silently choose the remote side of conflicting hunks and hide a real data or code conflict.
- [x] Separate fetch/build from commit/push.
- [x] Produce a build and source-health report before publishing.

### Phase 1 completion criteria

- [x] The raw cache has a verified, restorable archive.
- [x] The historical site can be rendered from preserved processed data without network access or source re-import.
- [x] Historical regression checks pass.
- [x] A failed or unchanged run does not create a misleading publication commit.

## Phase 2: create a source registry and health report

Sources differ enough in format and meaning that each source should have its own small downloader
and parser. Each parser produces a documented intermediate result through a common storage
interface. This keeps source-specific parsing separate from cross-source calculations and graph
generation.

SQLite is the preferred option to evaluate for the intermediate store because it supports typed
tables, joins, views, constraints, and reproducible queries without requiring a database server.
It is not mandatory: first implement a small pilot with one source and compare it with a simpler
file-based representation. Parsers should not contain calculation or graphing logic, and should
not depend directly on SQLite-specific details beyond the shared storage interface.

- [x] Add a machine-readable registry such as `sources.yaml` or `sources.json`.
- [x] Give every source a stable identifier independent of its URL.
- [x] Store provider, URL, format, expected update interval, and lifecycle status.
- [x] Store expected fields, units, geography, and date semantics.
- [x] Record which normalized metrics and graphs consume each source.
- [x] Record local-cache evidence, source publication date, and newest observation where the source provides them. A future downloader will record an authoritative successful-download timestamp.
- [x] Validate local file presence, non-empty content, schema, publication date, and newest observation. HTTP status, content type, and configured byte-size bounds belong to the Phase 3 download step.
- [x] Distinguish `active`, `frozen`, `retired`, `broken`, and `unknown`.
- [x] Generate a human-readable source-health report from the registry.
- [x] Confirm every row in the source inventory above.
- [x] Define a small common parser result containing source ID, observations, source dates, provenance, and warnings.
- [x] Give each active epidemiological source its own parser and a source-configured validated downloader; frozen and retired sources are deliberately not downloaded.
- [x] Keep source parsing separate from calculations, correlations, graphing, and publication for new adapters; migrate legacy parsing source by source in Phase 3.
- [x] Define a storage interface that supports inserting source observations and reading them for later calculations.
- [x] Pilot SQLite with one active source, including schema creation, idempotent imports, and a query used by an existing graph.
- [x] Decide between SQLite and a file-based intermediate store based on the pilot; record the decision before migrating other sources.
- [x] If SQLite is selected, keep the preserved JSON as the historical baseline and make the database rebuildable from preserved inputs and imports.

### Phase 2 completion criteria

- [x] Every external input has an owner, lifecycle state, and expected freshness (or an explicit null cadence for ended sources).
- [x] A stale but downloadable file is reported as stale, primarily from the newest observation or publication date in its contents; HTTP headers and local file times are secondary evidence.
- [x] The registry maps sources to metrics and graph consumers, and the health report explains source-level update failures.
- [x] Source parsing and cross-source calculations are separate processing stages for active sources; remaining legacy historical transformations read preserved caches only.
- [x] The intermediate-storage choice is documented by a completed pilot rather than assumed in advance.

## Phase 3: repair active sources

Implement and validate one source at a time.

- [x] Create one Markdown document per source, including frozen, retired, and broken sources where enough information is available.
- [x] For each source, document its owner, purpose, known URL history, schema, units, update cadence, observed date range, lifecycle status, parser, consumers, known gaps, and replacement decision.
- [x] Link source documents from the registry and from a source-documentation index.

### 3.1 Standard ingestion flow

For every active source:

- [x] Download to a temporary file.
- [x] Validate response status, content type, size, and schema.
- [x] Validate the source publication date and newest observation.
- [x] When downloaded content changes, save a dated immutable raw snapshot outside the normalized store.
- [x] Transform through a source-specific adapter.
- [x] Validate required fields, units, ranges, duplicate keys, date ordering, and expected date continuity as appropriate for each active source.
- [x] Classify validation results as fatal errors or warnings. Invalid structure, incompatible schema, or unsafe values are fatal; ordinary missing dates are normally warnings.
- [x] Preserve missing observations as gaps in reported source data. The 15 missing ARI values in the current feed are reported rather than interpolated.
- [x] Allow source-specific gap policies because daily, weekly, and irregularly sampled sources have different continuity expectations.
- [x] Merge through the common SQLite storage interface without changing unrelated historical observations; the legacy graph model preserves its baseline through 2024-09-23.
- [x] Record source dates, raw SHA-256, source path, and record count as provenance.
- [x] Make imports idempotent so processing the same raw snapshot twice produces no duplicate observations or unrelated changes.
- [x] Test with small committed wastewater, variant, and ARI fixtures.
- [x] Report source health and transformation results.

### 3.2 Suggested implementation order

- [x] Repair and validate wastewater ingestion.
- [x] Repair and validate variant ingestion.
- [x] Evaluate and implement the active ARI/Infectieradar feed as a distinct ARI metric.
- [x] Research current official hospital or respiratory-surveillance feeds.
- [x] Add only hospital feeds whose definitions can be clearly represented. Current SARI data was documented but not added because it is incompatible with historical COVID occupancy and no stable machine-readable feed was identified.
- [x] Disable repeated NICE requests after preserved history is verified.
- [x] Retire unused ECDC, Apple mobility, and old dashboard download paths from active execution.

### Phase 3 completion criteria

- [x] Active wastewater, variants, and ARI indicators update from authoritative RIVM sources.
- [x] Frozen and retired indicators remain unchanged; their final observation dates are recorded where available.
- [x] Source or schema failures stop publication and produce actionable errors.

## Phase 4: introduce a versioned data model

The current wide daily record combines metrics with different sources, units, date ranges, and lifecycles. Introduce a normalized representation without immediately deleting or rewriting the existing format.

Candidate observation shape:

```yaml
date: 2026-10-28
metric: wastewater_sars_cov_2
value: 123.4
unit: particles_per_100000_inhabitants
geography: NL
source_id: rivm_wastewater_national
source_publication_date: 2026-10-28
status: reported
provenance:
  raw_snapshot: path-or-checksum
  transformer_version: 1
```

- [ ] Define metric names, units, geography, null handling, and date semantics.
- [ ] Distinguish reported, revised, imputed, and calculated values.
- [ ] Add source and transformation provenance.
- [ ] Version the normalized schema.
- [ ] Write an adapter that reads the existing `daily-stats.json` format.
- [ ] Convert historical data into the new model without replacing the original.
- [ ] Compare old and new graph inputs metric by metric.
- [ ] Switch consumers only after parity is demonstrated.
- [ ] Document intentional differences.

### Phase 4 completion criteria

- [ ] New and historical observations share a documented, versioned model.
- [ ] Original files remain preserved.
- [ ] Every value used by the site can be traced to a source or calculation.

## Phase 5: refactor safely

- [ ] Separate download, validation, transformation, storage, charting, and publishing.
- [ ] Replace the large `brondata.py` workflow with explicit pipeline stages.
- [ ] Remove duplicate source downloads and transformations.
- [ ] Replace working-directory-relative paths with project-root-based paths.
- [ ] Define typed inputs and outputs for source adapters.
- [ ] Add unit tests for date parsing, merging, and source transforms.
- [ ] Add fixture-based tests using small samples from the preserved archive.
- [ ] Make chart generation deterministic where practical.
- [ ] Pin dependencies and document the supported Python version.
- [ ] Add a single documented local development command.
- [ ] Remove dead code only after coverage proves it is unused.

### Phase 5 completion criteria

- [ ] The pipeline stages can be run and tested independently.
- [ ] Source-specific changes do not require editing unrelated graph code.
- [ ] Historical regression tests still pass.

## Phase 6: update the site and automation

- [ ] Divide charts into current surveillance and historical COVID-19 sections.
- [ ] Show the source and latest observation date on every chart.
- [ ] Show an explicit final date for ended series.
- [ ] Label calculated or experimental metrics separately from reported data.
- [ ] Add a source-health/status page.
- [ ] Publish only when validated data or site content meaningfully changes.
- [ ] Run tests and validation before generating a publication commit.
- [ ] Keep page-hit collection outside the epidemiological build.
- [ ] Document manual recovery and rollback procedures.

### Phase 6 completion criteria

- [ ] Readers can tell which charts are current and which are historical.
- [ ] A publication identifies its source dates and pipeline health.
- [ ] Automation cannot silently publish stale or malformed data as current.

## Proposed milestones

### Milestone A: protected history

- [ ] External cache archive and committed manifest exist.
- [ ] Offline baseline build works.
- [ ] Unsafe automatic publishing is disabled.

### Milestone B: observable pipeline

- [x] Source registry exists.
- [x] Source-health report identifies active, stale, retired, and broken inputs.
- [ ] Historical regression tests run automatically.

### Milestone C: useful current data

- [x] Wastewater updates reliably.
- [x] Variants update reliably.
- [x] Current Infectieradar/ARI data is represented without rewriting old data.

### Milestone D: maintainable architecture

- [ ] Versioned observation model exists.
- [ ] Source adapters have fixtures and tests.
- [ ] Pipeline stages are separated.

### Milestone E: trustworthy publication

- [ ] Site distinguishes current and historical series.
- [ ] Publication is conditional on successful validation.
- [ ] Source status and last observation dates are visible.

## Decisions to make

Record decisions here as the work progresses.

| Decision | Options | Current preference | Status |
|---|---|---|---|
| Source registry format | YAML / JSON / Python | JSON avoids a new runtime dependency and is machine-readable | Decided: JSON |
| Normalized storage | JSON Lines / CSV / Parquet / SQLite | SQLite behind a storage interface; preserved JSON remains the historical baseline | Decided: SQLite |
| Historical graph compatibility | Pixel-identical / data-identical / documented differences | Data-identical | Open |
| Current hospital metric | Find compatible successor / introduce a distinctly named new metric / historical only | Do not join incompatible definitions | Open |
| Automation platform | Existing host / GitHub Actions / manual | Decide after the offline build is reliable | Open |

## Risks

| Risk | Mitigation |
|---|---|
| Refactoring changes historical numbers | Establish fixtures and regression tests first |
| A live-looking endpoint serves frozen data | Validate newest observation and expected cadence |
| Replacement source uses a different definition | Create a new metric instead of splicing the series |
| Raw cache is lost because it is ignored by Git | Keep the verified ZIP and SHA-256 file outside the repository |
| Provider revises old records | Preserve dated raw snapshots and record revisions explicitly |
| Generated output creates enormous diffs | Separate generated artifacts from source and meaningful data changes |
| Automation publishes partial results | Validate all required active sources before publication |

## Immediate next actions

These are the recommended first work items:

1. [x] Create and verify the external ZIP archive described in Phase 1.1.
2. [x] Build a read-only inventory tool for the registered external inputs.
3. [x] Generate source/date/schema health reports without modifying source data.
4. [x] Add an offline build command and capture its current failures.
5. [x] Add a small historical regression test suite.
6. [x] Change publishing so timestamp-only and failed runs do not commit.
7. [x] Create the source registry from the inventory table.
8. [x] Use wastewater as the parser/storage pilot; downloading current data remains Phase 3.

## Progress log

Add short dated entries rather than relying only on checked boxes.

| Date | Change | Result / follow-up |
|---|---|---|
| 2026-11-01 | Initial restoration plan created | Begin with the read-only data inventory |
| 2026-11-01 | Archived `cache/` and `data/` outside the repository | ZIP integrity verified; SHA-256 recorded in Phase 1.1 |
| 2026-11-01 | Added initial render-only path | Historical JSON remained unchanged; full render verification still required |
| 2026-11-01 | Verified the offline render | Completed with exit code 0 using the non-GUI backend; historical JSON checksum unchanged |
| 2026-11-01 | Added historical regression tests | Seven tests cover the baseline and build-health classification |
| 2026-11-01 | Separated update and publication | Update builds and reports health; publication is explicit and limited to generated data |
| 2026-11-01 | Added the source registry and health report | Required active caches are correctly reported stale and block publication |
| 2026-11-01 | Completed the wastewater SQLite pilot | 158,423 observations matched the in-memory graph query; re-import was idempotent |
| 2026-11-01 | Implemented validated active-source ingestion | Current wastewater, variants, and ARI feeds pass validation and have immutable raw snapshots |
| 2026-11-01 | Retired dead requests and reviewed hospital successors | NICE, ECDC, Apple, old dashboard, and frozen feeds are no longer requested; SARI remains a distinct future metric |
