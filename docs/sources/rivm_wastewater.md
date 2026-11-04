# RIVM national wastewater measurements per treatment plant

- Source ID: `rivm_wastewater`
- Owner/provider: RIVM
- Lifecycle: `active`
- Purpose/category: epidemiological
- Current URL: https://data.rivm.nl/covid-19/COVID-19_rioolwaterdata.json
- Metadata: https://data.rivm.nl/covid-19/COVID-19_rioolwaterdata.html
- URL history: only the current or final known URL is recorded; earlier URLs are not known unless noted below
- Format: `json`
- Update cadence: Every 7 day(s); stale after 14 day(s)
- Observed date range: 2020-03-30 through 2026-10-25
- Observation date field: `Date_measurement`
- Publication date field: `Date_of_report`
- Required fields: `Version`, `Date_of_report`, `Date_measurement`, `RWZI_AWZI_code`, `RWZI_AWZI_name`, `RNA_flow_per_100000`
- Units: `virus particles per 100,000 inhabitants`
- Geography: wastewater treatment plant, aggregated nationally
- Parser: `scripts.pipeline.wastewater`
- Normalized metrics: `RNA.RNA_per_100k_avg`, `RNA.besmettelijk`
- Consumers: `scripts/createRNAGraph.py`, `scripts/modules/calculate_geschat_ziek.py`

## Known gaps and decision

No source-specific gap is recorded beyond the lifecycle and observed range above.

Replacement decision: Keep and validate before installation.
