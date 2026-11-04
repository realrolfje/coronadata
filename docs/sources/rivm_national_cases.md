# RIVM national case-level data

- Source ID: `rivm_national_cases`
- Owner/provider: RIVM
- Lifecycle: `frozen`
- Purpose/category: epidemiological
- Current URL: https://data.rivm.nl/covid-19/COVID-19_casus_landelijk.json
- URL history: only the current or final known URL is recorded; earlier URLs are not known unless noted below
- Format: `json`
- Update cadence: Ended or not established
- Observed date range: Through 2023-03-31 (start not recorded in the registry)
- Observation date field: `Date_statistics`
- Publication date field: `Date_file`
- Required fields: `Date_file`, `Date_statistics`, `Agegroup`, `Deceased`, `Municipal_health_service`
- Units: `cases`
- Geography: Netherlands and municipal health service
- Parser: `scripts/modules/download_casus_landelijk.py`
- Normalized metrics: `positief`, `overleden`, `besmettingleeftijd`
- Consumers: `scripts/createHeatmap.py`, `scripts/createZiekGraph.py`

## Known gaps and decision

No source-specific gap is recorded beyond the lifecycle and observed range above.

Replacement decision: Preserve the final observations and do not request the source during normal builds.
