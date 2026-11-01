# LCPS hospital and ICU COVID datafeed

- Source ID: `lcps_datafeed`
- Owner/provider: LCPS/LNAZ
- Lifecycle: `frozen`
- Purpose/category: hospital surveillance
- Current URL: https://lcps.nu/wp-content/uploads/covid-19-datafeed.csv
- Metadata: https://lcps.nu/datafeed/
- URL history: only the current or final known URL is recorded; earlier URLs are not known unless noted below
- Format: `csv`
- Update cadence: Ended or not established
- Observed date range: Through 2024-06-01 (start not recorded in the registry)
- Observation date field: `datum`
- Publication date field: `Not available`
- Required fields: `datum`, `IC_bezetting_covid`, `kliniek_bezetting_covid`
- Units: `occupied beds`, `admissions`
- Geography: Netherlands
- Parser: `scripts/modules/download_lcps_ziekenhuisopnames.py`
- Normalized metrics: `nu_op_ic`, `nu_opgenomen`
- Consumers: `scripts/createZiekenhuisTotaalGraph.py`, `scripts/createZiekGraph.py`

## Known gaps and decision

LCPS stopped adding national daily COVID figures from June 2024.

Replacement decision: Keep the COVID hospital series frozen. Current SARI surveillance has a different definition and must not be spliced into it.
