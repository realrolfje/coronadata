# RIVM performed tests

- Source ID: `rivm_tests`
- Owner/provider: RIVM
- Lifecycle: `frozen`
- Purpose/category: epidemiological
- Current URL: https://data.rivm.nl/covid-19/COVID-19_uitgevoerde_testen.json
- URL history: only the current or final known URL is recorded; earlier URLs are not known unless noted below
- Format: `json`
- Update cadence: Ended or not established
- Observed date range: Through 2023-03-17 (start not recorded in the registry)
- Observation date field: `Date_of_statistics`
- Publication date field: `Date_of_report`
- Required fields: `Date_of_report`, `Date_of_statistics`, `Tested_positive`, `Tested_with_result`
- Units: `tests`, `positive tests`
- Geography: security region
- Parser: `scripts/modules/brondata.py`
- Normalized metrics: `rivm_totaal_tests`, `rivm_totaal_tests_positief`
- Consumers: `scripts/createCovidTestsGraph.py`

## Known gaps and decision

No source-specific gap is recorded beyond the lifecycle and observed range above.

Replacement decision: Preserve the final observations and do not request the source during normal builds.
