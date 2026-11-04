# RIVM/NICE weekly SARI ICU admissions

- Source ID: `rivm_nice_sari`
- Owner/provider: RIVM/NICE
- Lifecycle: `active`
- Purpose/category: respiratory surveillance
- Current URL: https://data.rivm.nl/opendata/api/3/action/package_show?id=res-ari-surveillance
- Metadata: https://www.rivm.nl/luchtweginfecties/sari
- URL history: only the current or final known URL is recorded; earlier URLs are not known unless noted below
- Format: `csv`
- Update cadence: Every 7 day(s); stale after 21 day(s)
- Observed date range: Derived from the local cache by `scripts/sourceInventory.py` when actively scanned
- Observation date field: `season/week`
- Publication date field: `Not available`
- Required fields: `season`, `week`, `value`
- Units: `IC admissions per week`
- Geography: Netherlands
- Parser: `scripts/pipeline/sari.py`
- Normalized metrics: `sari_icu_admissions_weekly`
- Consumers: `scripts/createSariGraph.py`

## Known gaps and decision

Weekly severe acute respiratory infection ICU admissions; recent weeks can be revised and ICU coverage varies.

Replacement decision: Keep and validate before installation.
