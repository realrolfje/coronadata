# RIVM SARS-CoV-2 variants

- Source ID: `rivm_variants`
- Owner/provider: RIVM
- Lifecycle: `active`
- Purpose/category: epidemiological
- Current URL: https://data.rivm.nl/covid-19/COVID-19_varianten.json
- Metadata: https://data.rivm.nl/covid-19/COVID-19_varianten.html
- URL history: only the current or final known URL is recorded; earlier URLs are not known unless noted below
- Format: `json`
- Update cadence: Every 28 day(s); stale after 45 day(s)
- Observed date range: 2020-11-30 through 2026-10-19
- Observation date field: `Date_of_statistics_week_start`
- Publication date field: `Date_of_report`
- Required fields: `Version`, `Date_of_report`, `Date_of_statistics_week_start`, `Variant_code`, `Variant_name`, `Sample_size`, `Variant_cases`
- Units: `samples`, `variant cases`
- Geography: Netherlands
- Parser: `scripts.pipeline.variants`
- Normalized metrics: `varianten`
- Consumers: `scripts/createVariantenGraph.py`

## Known gaps and decision

No source-specific gap is recorded beyond the lifecycle and observed range above.

Replacement decision: Keep and validate before installation.
