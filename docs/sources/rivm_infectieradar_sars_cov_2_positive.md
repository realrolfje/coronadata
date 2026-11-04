# RIVM Infectieradar weekly SARS-CoV-2 positive percentage

- Source ID: `rivm_infectieradar_sars_cov_2_positive`
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
- Units: `percent of participants`
- Geography: Netherlands
- Parser: `scripts/pipeline/weekly_trend.py`
- Normalized metrics: `infectieradar_sars_cov_2_positive_percentage`
- Consumers: Not available

## Known gaps and decision

Stored as an input for a future current trend indicator; not interpreted as a reproduction number.

Replacement decision: Keep and validate before installation.
