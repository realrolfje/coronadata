# ECDC ERVISS Dutch non-sentinel SARS-CoV-2 detections

- Source ID: `ecdc_erviss_nl_sars_cov_2_detections`
- Owner/provider: ECDC
- Lifecycle: `active`
- Purpose/category: respiratory surveillance
- Current URL: https://raw.githubusercontent.com/EU-ECDC/Respiratory_viruses_weekly_data/main/data/nonSentinelTestsDetections.csv
- Metadata: https://github.com/EU-ECDC/Respiratory_viruses_weekly_data
- URL history: only the current or final known URL is recorded; earlier URLs are not known unless noted below
- Format: `csv`
- Update cadence: Every 7 day(s); stale after 21 day(s)
- Observed date range: Derived from the local cache by `scripts/sourceInventory.py` when actively scanned
- Observation date field: `yearweek`
- Publication date field: `Not available`
- Required fields: `survtype`, `countryname`, `yearweek`, `pathogen`, `indicator`, `age`, `value`
- Units: `positive samples per week`
- Geography: Netherlands (file covers all reporting countries)
- Parser: `scripts/pipeline/erviss.py`
- Normalized metrics: `erviss_sars_cov_2_detections_weekly`
- Consumers: `scripts/createLaboratoriumGraph.py`

## Known gaps and decision

Dutch non-sentinel SARS-CoV-2 detections as reported to ECDC. The counts differ from the RIVM laboratory series and are shown as a separate line, not merged.

Replacement decision: Keep and validate before installation.
