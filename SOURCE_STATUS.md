# Source health

Generated from `sources.json` by `scripts/sourceInventory.py`.

Overall status: **healthy**

| Source | Lifecycle | Health | Newest observation | Publication | Cache |
|---|---|---|---|---|---|
| RIVM national wastewater measurements per treatment plant | active | healthy | 2026-10-25 | 2026-10-28 | `cache/COVID-19_rioolwaterdata.json` |
| RIVM SARS-CoV-2 variants | active | healthy | 2026-10-19 | 2026-10-28 | `cache/COVID-19_varianten.json` |
| RIVM Infection Radar acute respiratory symptoms | active | healthy | 2026-10-27 | 2026-10-28 | `cache/ARI_Infectieradar_symptomen_per_dag.json` |
| RIVM Infection Radar COVID-like symptoms | frozen | frozen | 2023-10-31 | — | `cache/COVID-19_Infectieradar_symptomen_per_dag.json` |
| RIVM reproduction number | frozen | frozen | 2023-07-09 | — | `cache/COVID-19_reproductiegetal.json` |
| RIVM national case-level data | frozen | frozen | 2023-03-31 | — | `cache/COVID-19_casus_landelijk.json` |
| RIVM performed tests | frozen | frozen | 2023-03-17 | — | `cache/COVID-19_uitgevoerde_testen.json` |
| CoronaWatchNL historical RIVM tests | frozen | frozen | 2021-01-31 | — | `cache/J535D165-RIVM_NL_test_latest.csv` |
| RIVM estimated infectious population | frozen | frozen | 2021-07-04 | — | `cache/COVID-19_prevalentie.json` |
| RIVM vaccination coverage by municipality, week and age | frozen | frozen | 2023-09-18 | — | `cache/COVID-19_vaccinatiegraad_per_gemeente_per_week_leeftijd.json` |
| RIVM/NICE weekly SARI ICU admissions | active | healthy | 2026-10-19 | — | `cache/rivm-nice-sari-weekly-admissions.csv` |
| RIVM weekly national SARS-CoV-2 wastewater trend | active | healthy | 2026-10-19 | — | `cache/rivm-sars-cov-2-wastewater-weekly.csv` |
| RIVM Infectieradar weekly SARS-CoV-2 positive percentage | active | healthy | 2026-10-19 | — | `cache/rivm-infectieradar-sars-cov-2-positive-weekly.csv` |
| RIVM Virological Weekly Reports SARS-CoV-2 positive percentage | active | healthy | 2026-10-19 | — | `cache/rivm-laboratory-sars-cov-2-positive-weekly.csv` |
| RIVM Virological Weekly Reports SARS-CoV-2 positive samples | active | healthy | 2026-10-19 | — | `cache/rivm-laboratory-sars-cov-2-detections-weekly.csv` |
| ECDC ERVISS Dutch non-sentinel SARS-CoV-2 detections | active | healthy | 2026-10-19 | — | `cache/ecdc-erviss-non-sentinel-tests-detections.csv` |
| LCPS hospital and ICU COVID datafeed | frozen | frozen | 2024-05-31 | — | `cache/covid-19-datafeed.csv` |
| LCPS legacy hospital CSV | frozen | frozen | 2021-07-26 | — | `cache/lcps-covid-19.csv` |
| NICE current ICU COVID occupancy | retired | retired | 2023-11-01 | — | `cache/NICE-intake-count.json` |
| NICE cumulative ICU COVID intake | retired | missing | — | — | `cache/NICE-intake-cumulative.json` |
| NICE current ward COVID occupancy | retired | retired | 2023-11-01 | — | `cache/NICE-zkh-intake-count.json` |
| Dutch government coronavirus dashboard JSON | retired | retired | — | — | `cache/rijksoverheid-coronadashboard-NL.json` |
| Apple mobility trends | retired | retired | — | — | `—` |
| ECDC coordinated travel restriction map | retired | retired | — | — | `docs/extern/ECDC_Subnational_Combined_traffic.png` |
| Website page-hit counter | active | unverified | — | — | `data/pagehits.csv` |

## Details

- **nice_intake_cumulative**: Local cache file is missing.
- **apple_mobility**: No local cache path is configured.
