import hashlib
import json
from pathlib import Path

from .models import Observation, ParserResult


TRANSFORMER_VERSION = 1

# Graph-facing scalar fields in the wide compatibility model. Null values are absent observations;
# numeric zero remains a value because the legacy graphs distinguish it from null in some series.
METRIC_SPECS = {
    "positief": ("covid_cases_daily", "persons", "rivm_national_cases", "reported"),
    "totaal_positief": ("covid_cases_cumulative", "persons", "derived_coronadata", "calculated"),
    "nu_op_ic": ("covid_icu_occupancy", "persons", "nice_intake_count", "reported"),
    "nu_op_ic_lcps": ("covid_icu_occupancy_lcps", "persons", "lcps_legacy_feed", "reported"),
    "nu_op_ic_noncovid_lcps": ("noncovid_icu_occupancy_lcps", "persons", "lcps_legacy_feed", "reported"),
    "geweest_op_ic": ("covid_icu_intake_cumulative", "persons", "nice_intake_cumulative", "reported"),
    "opgenomen": ("covid_hospital_admissions_daily", "persons", "rivm_national_cases", "reported"),
    "nu_opgenomen": ("covid_ward_occupancy", "persons", "nice_hospital_count", "reported"),
    "nu_opgenomen_lcps": ("covid_ward_occupancy_lcps", "persons", "lcps_legacy_feed", "reported"),
    "totaal_opgenomen": ("covid_hospital_admissions_cumulative", "persons", "derived_coronadata", "calculated"),
    "overleden": ("covid_deaths_daily", "persons", "rivm_national_cases", "reported"),
    "totaal_overleden": ("covid_deaths_cumulative", "persons", "derived_coronadata", "calculated"),
    "Rt_avg": ("covid_reproduction_number", "ratio", "rivm_reproduction_number", "reported"),
    "Rt_low": ("covid_reproduction_number_low", "ratio", "rivm_reproduction_number", "reported"),
    "Rt_up": ("covid_reproduction_number_high", "ratio", "rivm_reproduction_number", "reported"),
    "Rt_population": ("covid_reproduction_population", "persons", "rivm_reproduction_number", "reported"),
    "RNA.totaal_RNA_per_100k": ("wastewater_rna_flow_sum", "virus_particles_per_100000_inhabitants", "rivm_wastewater", "calculated"),
    "RNA.totaal_RNA_metingen": ("wastewater_measurement_count", "measurements", "rivm_wastewater", "calculated"),
    "RNA.RNA_per_100k_avg": ("wastewater_rna_flow_average", "virus_particles_per_100000_inhabitants", "rivm_wastewater", "calculated"),
    "RNA.besmettelijk": ("estimated_infectious_from_wastewater", "persons", "derived_coronadata", "calculated"),
    "RNA.besmettelijk_error": ("estimated_infectious_from_wastewater_error", "ratio", "derived_coronadata", "calculated"),
    "RNA.populatie_dekking": ("wastewater_population_coverage", "percent", "rivm_wastewater", "calculated"),
    "rivm_totaal_tests": ("covid_tests_daily", "tests", "rivm_tests", "reported"),
    "rivm_totaal_tests         ": ("covid_tests_daily_legacy_key", "tests", "rivm_tests", "reported"),
    "rivm_totaal_tests_positief": ("covid_positive_tests_daily", "tests", "rivm_tests", "reported"),
    "rivm_totaal_personen_getest": ("covid_persons_tested_weekly", "persons", "coronawatch_tests", "reported"),
    "rivm_totaal_personen_positief": ("covid_persons_positive_weekly", "persons", "coronawatch_tests", "reported"),
    "rivm_aantal_testlabs": ("covid_reporting_test_labs", "laboratories", "coronawatch_tests", "reported"),
    "rivm_infectieradar_perc": ("infectieradar_covid_symptoms_percentage", "percent_of_participants", "rivm_infectieradar_covid", "reported"),
    "rivm_infectieradar_ari_perc": ("infectieradar_ari_symptoms_percentage", "percent_of_participants", "rivm_infectieradar_ari", "reported"),
    "rivm_schatting_besmettelijk.min": ("rivm_estimated_infectious_low", "persons", "rivm_prevalence", "reported"),
    "rivm_schatting_besmettelijk.value": ("rivm_estimated_infectious", "persons", "rivm_prevalence", "reported"),
    "rivm_schatting_besmettelijk.max": ("rivm_estimated_infectious_high", "persons", "rivm_prevalence", "reported"),
    "besmettingleeftijd_gemiddeld": ("covid_case_mean_age", "years", "derived_coronadata", "calculated"),
    "mobiliteit.lopen": ("mobility_walking", "index", "apple_mobility", "reported"),
    "mobiliteit.ov": ("mobility_transit", "index", "apple_mobility", "reported"),
    "mobiliteit.rijden": ("mobility_driving", "index", "apple_mobility", "reported"),
    "rolf_besmettelijk": ("estimated_infectious_coronadata", "persons", "derived_coronadata", "calculated"),
}

for vaccine in ("astra_zeneca", "pfizer", "cure_vac", "janssen", "moderna", "sanofi", "totaal", "totaal_mensen", "totaal_geschat", "totaal_mensen_geschat", "geleverd"):
    METRIC_SPECS[f"vaccinaties.{vaccine}"] = (
        f"vaccinations_{vaccine}", "doses", "rivm_vaccination_coverage", "reported"
    )


def nested_value(record, path):
    value = record
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def parse(filename):
    path = Path(filename)
    raw = path.read_bytes()
    daily = json.loads(raw)
    observations = []
    for date, record in daily.items():
        for field, (metric, unit, source_id, status) in METRIC_SPECS.items():
            value = nested_value(record, field)
            if value is None or isinstance(value, bool):
                continue
            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                continue
            observations.append(Observation(
                source_id=source_id, metric=metric, date=date, value=numeric_value,
                unit=unit, status=status,
                provenance={"legacy_field": field, "transformer": "legacy_daily_stats"},
            ))

        for age_group, count in record.get("besmettingleeftijd", {}).items():
            observations.append(Observation(
                source_id="rivm_national_cases", metric="covid_cases_by_age_group",
                date=date, value=float(count), unit="persons", status="reported",
                dimensions={"age_group": age_group},
                provenance={"legacy_field": f"besmettingleeftijd.{age_group}", "transformer": "legacy_daily_stats"},
            ))

        for code, variant in record.get("varianten", {}).items():
            for field, unit in (("cases", "sequenced_samples"), ("sample_size", "sequenced_samples")):
                value = variant.get(field)
                if value is not None:
                    observations.append(Observation(
                        source_id="rivm_variants", metric=f"sars_cov_2_variant_{field}",
                        date=date, value=float(value), unit=unit, status="reported",
                        dimensions={"variant_code": code, "variant_name": variant.get("name")},
                        provenance={"legacy_field": f"varianten.{code}.{field}", "transformer": "legacy_daily_stats"},
                    ))

    return ParserResult(
        source_id="legacy_daily_stats",
        observations=observations,
        newest_observation=max(daily) if daily else None,
        provenance={
            "sha256": hashlib.sha256(raw).hexdigest(),
            "path": str(path),
            "transformer": "legacy_daily_stats",
            "transformer_version": TRANSFORMER_VERSION,
            "schema_version": 1,
        },
    )
