# LCPS legacy hospital CSV

- Source ID: `lcps_legacy_feed`
- Owner/provider: LCPS/LNAZ
- Lifecycle: `frozen`
- Purpose/category: hospital surveillance
- Current URL: https://lcps.nu/wp-content/uploads/covid-19.csv
- URL history: only the current or final known URL is recorded; earlier URLs are not known unless noted below
- Format: `csv`
- Update cadence: Ended or not established
- Observed date range: Through 2021-07-26 (start not recorded in the registry)
- Observation date field: `Datum`
- Publication date field: `Not available`
- Required fields: `Datum`, `IC_Bedden_COVID`, `IC_Bedden_Non_COVID`, `Kliniek_Bedden`
- Units: `occupied beds`, `admissions`
- Geography: Netherlands
- Parser: `scripts/modules/brondata.py`
- Normalized metrics: `nu_op_ic_lcps`, `nu_op_ic_noncovid_lcps`, `nu_opgenomen_lcps`
- Consumers: `scripts/createZiekGraph.py`

## Known gaps and decision

No source-specific gap is recorded beyond the lifecycle and observed range above.

Replacement decision: Keep the COVID hospital series frozen. Current SARI surveillance has a different definition and must not be spliced into it.
