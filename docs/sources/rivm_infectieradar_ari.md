# RIVM Infection Radar acute respiratory symptoms

- Source ID: `rivm_infectieradar_ari`
- Owner/provider: RIVM
- Lifecycle: `active`
- Purpose/category: respiratory surveillance
- Current URL: https://data.rivm.nl/covid-19/ARI_Infectieradar_symptomen_per_dag.json
- Metadata: https://data.rivm.nl/covid-19/ARI_Infectieradar_symptomen_per_dag.html
- URL history: only the current or final known URL is recorded; earlier URLs are not known unless noted below
- Format: `json`
- Update cadence: Every 7 day(s); stale after 14 day(s)
- Observed date range: 2020-11-01 through 2026-10-27
- Observation date field: `Date_of_statistics`
- Publication date field: `Date_of_report`
- Required fields: `Version`, `Date_of_report`, `Date_of_statistics`
- Units: `percentage of participants`
- Geography: Netherlands
- Parser: `scripts.pipeline.infectieradar_ari`
- Normalized metrics: `rivm_infectieradar_ari_perc`
- Consumers: `scripts/createSchattingAfwijkingGraph.py`

## Known gaps and decision

Implemented as a distinct acute-respiratory-symptoms metric; it is not joined to the frozen COVID-like-symptoms series.

Replacement decision: Keep and validate before installation.
