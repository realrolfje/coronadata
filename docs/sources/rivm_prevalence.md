# RIVM estimated infectious population

- Source ID: `rivm_prevalence`
- Owner/provider: RIVM
- Lifecycle: `frozen`
- Purpose/category: derived epidemiological estimate
- Current URL: https://data.rivm.nl/covid-19/COVID-19_prevalentie.json
- URL history: only the current or final known URL is recorded; earlier URLs are not known unless noted below
- Format: `json`
- Update cadence: Ended or not established
- Observed date range: Through 2021-07-04 (start not recorded in the registry)
- Observation date field: `Date`
- Publication date field: `Not available`
- Required fields: `Date`, `prev_low`, `prev_avg`, `prev_up`
- Units: `estimated infectious persons`
- Geography: Netherlands
- Parser: `scripts/modules/brondata.py`
- Normalized metrics: `rivm_schatting_besmettelijk`
- Consumers: `scripts/createZiekGraph.py`, `scripts/createSchattingAfwijkingGraph.py`

## Known gaps and decision

No source-specific gap is recorded beyond the lifecycle and observed range above.

Replacement decision: Preserve the final observations and do not request the source during normal builds.
