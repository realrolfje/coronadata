# NICE current ICU COVID occupancy

- Source ID: `nice_intake_count`
- Owner/provider: Stichting NICE
- Lifecycle: `retired`
- Purpose/category: hospital surveillance
- Current URL: https://www.stichting-nice.nl/covid-19/public/intake-count/
- URL history: only the current or final known URL is recorded; earlier URLs are not known unless noted below
- Format: `json`
- Update cadence: Ended or not established
- Observed date range: Through 2023-11-01 (start not recorded in the registry)
- Observation date field: `date`
- Publication date field: `Not available`
- Required fields: `date`, `value`
- Units: `patients`
- Geography: Netherlands
- Parser: `scripts/modules/download_Zkh.py`
- Normalized metrics: `nu_op_ic`
- Consumers: `scripts/createZiekGraph.py`

## Known gaps and decision

No source-specific gap is recorded beyond the lifecycle and observed range above.

Replacement decision: Keep the COVID hospital series frozen. Current SARI surveillance has a different definition and must not be spliced into it.
