# RIVM vaccination coverage by municipality, week and age

- Source ID: `rivm_vaccination_coverage`
- Owner/provider: RIVM
- Lifecycle: `frozen`
- Purpose/category: epidemiological
- Current URL: https://data.rivm.nl/covid-19/COVID-19_vaccinatiegraad_per_gemeente_per_week_leeftijd.json
- URL history: only the current or final known URL is recorded; earlier URLs are not known unless noted below
- Format: `json`
- Update cadence: Ended or not established
- Observed date range: Through 2023-09-18 (start not recorded in the registry)
- Observation date field: `Date_of_statistics`
- Publication date field: `Date_of_report`
- Required fields: `Date_of_report`, `Date_of_statistics`, `Region_code`, `Age_group`
- Units: `coverage percentage`
- Geography: municipality
- Parser: `No parser; source is unused or awaiting a decision`
- Normalized metrics: Not available
- Consumers: Not available

## Known gaps and decision

Downloaded but not currently transformed by the combined pipeline.

Replacement decision: Preserve the final observations and do not request the source during normal builds.
