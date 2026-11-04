from dataclasses import dataclass
from math import log
from statistics import mean

from scipy.signal import savgol_filter


@dataclass(frozen=True)
class CalculationReport:
    name: str
    observations_written: int
    warnings: tuple[str, ...] = ()


def smooth(values, iterations=2, window=13, order=1):
    output = list(values)
    if len(output) < window:
        return output
    for _ in range(iterations):
        output = savgol_filter(output, window, order)
    return output


def calculate_wastewater_estimate(daily: dict) -> CalculationReport:
    dates = [
        date for date, record in daily.items()
        if record["RNA"]["totaal_RNA_metingen"] > 30
    ]
    rna = smooth([daily[date]["RNA"]["RNA_per_100k_avg"] for date in dates])
    ratios = []
    for index, date in enumerate(dates):
        estimate = daily[date]["rivm_schatting_besmettelijk"]["value"]
        if estimate and estimate > 5000 and rna[index] > 1000:
            ratios.append(estimate / rna[index])
    if not ratios:
        return CalculationReport(
            "wastewater_estimate", 0, ("no overlap with RIVM prevalence estimate",)
        )
    scale = mean(ratios)
    for index, date in enumerate(dates):
        daily[date]["RNA"]["besmettelijk"] = max(1, rna[index] * scale)
    return CalculationReport("wastewater_estimate", len(dates))


def calculate_mean_case_age(daily: dict) -> CalculationReport:
    written = 0
    for record in daily.values():
        count = sum(record["besmettingleeftijd"].values())
        if count:
            weighted = sum(
                number * int(age)
                for age, number in record["besmettingleeftijd"].items()
            )
            record["besmettingleeftijd_gemiddeld"] = weighted / count
            written += 1
    return CalculationReport("mean_case_age", written)


def calculate_cumulative_totals(daily: dict) -> CalculationReport:
    cases = admissions = deaths = 0
    for record in daily.values():
        cases += record["positief"]
        admissions += record["nu_opgenomen"]
        deaths += record["overleden"]
        record["totaal_positief"] = cases
        record["totaal_opgenomen"] = admissions
        record["totaal_overleden"] = deaths
    return CalculationReport("cumulative_totals", len(daily) * 3)


def calculate_coronadata_estimate(daily: dict) -> CalculationReport:
    dates = []
    values = []
    for date, record in daily.items():
        sample_size = record.get("rivm_totaal_tests", 0) or 0
        cases = record.get("rivm_totaal_tests_positief", 0) or 0
        if sample_size == 0:
            for sample in record["varianten"].values():
                sample_size += sample.get("sample_size", 0)
                cases += sample.get("cases", 0)
        total_rna = record["RNA"]["totaal_RNA_per_100k"] or 0
        if sample_size == 0 or total_rna <= 1:
            continue
        dates.append(date)
        values.append(
            ((1_000_000 * cases / sample_size) + (3 * sample_size) + (22 * cases))
            * log(total_rna, 10) / 44
        )
    values = smooth(values)
    for date, value in zip(dates, values):
        daily[date]["rolf_besmettelijk"] = value
    return CalculationReport("coronadata_estimate", len(dates))


def run_calculations(daily: dict) -> list[CalculationReport]:
    return [
        calculate_wastewater_estimate(daily),
        calculate_mean_case_age(daily),
        calculate_cumulative_totals(daily),
        calculate_coronadata_estimate(daily),
    ]
