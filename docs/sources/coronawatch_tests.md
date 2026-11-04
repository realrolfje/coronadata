# CoronaWatchNL historical RIVM tests

- Source ID: `coronawatch_tests`
- Owner/provider: CoronaWatchNL
- Lifecycle: `frozen`
- Purpose/category: historical mirror
- Current URL: https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data-misc/data-test/RIVM_NL_test_latest.csv
- URL history: only the current or final known URL is recorded; earlier URLs are not known unless noted below
- Format: `csv`
- Update cadence: Ended or not established
- Observed date range: Through 2021-01-31 (start not recorded in the registry)
- Observation date field: `EindDatum`
- Publication date field: `Not available`
- Required fields: `Jaar`, `Week`, `BeginDatum`, `EindDatum`, `Type`, `Aantal`
- Units: `persons tested`
- Geography: Netherlands
- Parser: `scripts/modules/brondata.py`
- Normalized metrics: `rivm_totaal_personen_getest`, `rivm_totaal_personen_positief`
- Consumers: `scripts/createCovidTestsGraph.py`

## Known gaps and decision

No source-specific gap is recorded beyond the lifecycle and observed range above.

Replacement decision: Preserve the final observations and do not request the source during normal builds.
