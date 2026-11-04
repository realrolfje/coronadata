# RIVM Infection Radar COVID-like symptoms

- Source ID: `rivm_infectieradar_covid`
- Owner/provider: RIVM
- Lifecycle: `frozen`
- Purpose/category: epidemiological
- Current URL: https://data.rivm.nl/covid-19/COVID-19_Infectieradar_symptomen_per_dag.json
- URL history: only the current or final known URL is recorded; earlier URLs are not known unless noted below
- Format: `json`
- Update cadence: Ended or not established
- Observed date range: Through 2023-10-31 (start not recorded in the registry)
- Observation date field: `Date_of_statistics`
- Publication date field: `Date_of_report`
- Required fields: `Date_of_report`, `Date_of_statistics`, `Perc_covid_symptoms`
- Units: `percentage of participants`
- Geography: Netherlands
- Parser: `scripts/modules/brondata.py`
- Normalized metrics: `rivm_infectieradar_perc`
- Consumers: `scripts/processTemplates.py`

## Known gaps and decision

No source-specific gap is recorded beyond the lifecycle and observed range above.

Replacement decision: Keep this COVID-specific series frozen. ARI Infectieradar is a distinct metric, not a continuation.
