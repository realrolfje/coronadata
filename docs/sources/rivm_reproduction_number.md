# RIVM reproduction number

- Source ID: `rivm_reproduction_number`
- Owner/provider: RIVM
- Lifecycle: `frozen`
- Purpose/category: epidemiological
- Current URL: https://data.rivm.nl/covid-19/COVID-19_reproductiegetal.json
- URL history: only the current or final known URL is recorded; earlier URLs are not known unless noted below
- Format: `json`
- Update cadence: Ended or not established
- Observed date range: Through 2023-07-09 (start not recorded in the registry)
- Observation date field: `Date`
- Publication date field: `Not available`
- Required fields: `Date`, `Rt_avg`, `Rt_low`, `Rt_up`
- Units: `reproduction number`
- Geography: Netherlands
- Parser: `scripts/modules/download_Rt.py`
- Normalized metrics: `Rt_avg`, `Rt_low`, `Rt_up`
- Consumers: `scripts/createRtGraph.py`

## Known gaps and decision

No source-specific gap is recorded beyond the lifecycle and observed range above.

Replacement decision: Preserve the final observations and do not request the source during normal builds.
