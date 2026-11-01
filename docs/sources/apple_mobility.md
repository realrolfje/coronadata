# Apple mobility trends

- Source ID: `apple_mobility`
- Owner/provider: Apple
- Lifecycle: `retired`
- Purpose/category: mobility
- Current URL: https://covid19-static.cdn-apple.com/covid19-mobility-data/2210HotfixDev16/v3/en-us/applemobilitytrends-2022-03-26.csv
- URL history: only the current or final known URL is recorded; earlier URLs are not known unless noted below
- Format: `csv`
- Update cadence: Ended or not established
- Observed date range: Derived from the local cache by `scripts/sourceInventory.py` when actively scanned
- Observation date field: `Not available`
- Publication date field: `Not available`
- Required fields: Not available
- Units: `relative mobility index`
- Geography: Netherlands
- Parser: `scripts/modules/brondata.py`
- Normalized metrics: `mobiliteit`
- Consumers: `scripts/createMobilityGraph.py`

## Known gaps and decision

The fixed URL points to the final archived Apple report and is not called by the combined pipeline.

Replacement decision: Do not request the source; retain preserved historical artifacts only.
