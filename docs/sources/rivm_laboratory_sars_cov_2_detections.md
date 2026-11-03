# RIVM Virological Weekly Reports SARS-CoV-2 positive samples

- Source ID: `rivm_laboratory_sars_cov_2_detections`
- Owner/provider: RIVM
- Lifecycle: `active`
- Purpose/category: respiratory surveillance
- Current URL: https://data.rivm.nl/opendata/api/3/action/package_show?id=res-ari-surveillance
- Metadata: https://www.rivm.nl/corona/actueel/weekcijfers
- URL history: only the current or final known URL is recorded; earlier URLs are not known unless noted below
- Format: `csv`
- Update cadence: Every 7 day(s); stale after 21 day(s)
- Observed date range: Derived from the local cache by `scripts/sourceInventory.py` when actively scanned
- Observation date field: `season/week`
- Publication date field: `Not available`
- Required fields: `season`, `week`, `value`
- Units: `positive samples per week`
- Geography: Netherlands
- Parser: `scripts/pipeline/weekly_trend.py`
- Normalized metrics: `laboratory_sars_cov_2_detections_weekly`
- Consumers: `scripts/createLaboratoriumGraph.py`

## Known gaps and decision

This series is the weekly number of positive SARS-CoV-2 samples reported by laboratories of the Dutch Working Group for Clinical Virology (NWKV).

Replacement decision: Keep and validate before installation.
