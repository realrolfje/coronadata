from dataclasses import dataclass
import csv
import datetime
import json
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class TransformReport:
    name: str
    records_read: int
    observations_written: int
    warnings: tuple[str, ...] = ()


def _integer_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _integer_or_zero(value):
    return _integer_or_none(value) or 0


def transform_prevalence(path: Path, daily: dict) -> TransformReport:
    records = json.loads(path.read_text())
    written = 0
    warnings = []
    for record in records:
        date = record["Date"]
        if date not in daily:
            continue
        try:
            target = daily[date]["rivm_schatting_besmettelijk"]
            target["min"] = int(record["prev_low"])
            target["max"] = int(record["prev_up"])
            target["value"] = int(record["prev_avg"])
            written += 3
        except (TypeError, ValueError, KeyError) as error:
            warnings.append(f"{date}: {error}")
    return TransformReport("rivm_prevalence", len(records), written, tuple(warnings))


def transform_legacy_infectieradar(path: Path, daily: dict) -> TransformReport:
    records = json.loads(path.read_text())
    written = 0
    warnings = []
    for record in records:
        date = record["Date_of_statistics"]
        if date not in daily or record.get("Perc_covid_symptoms") is None:
            continue
        try:
            daily[date]["rivm_infectieradar_perc"] = float(record["Perc_covid_symptoms"])
            written += 1
        except (TypeError, ValueError) as error:
            warnings.append(f"{date}: {error}")
    return TransformReport("rivm_infectieradar_covid", len(records), written, tuple(warnings))


def transform_coronawatch_tests(
    path: Path, daily: dict, ensure_record: Callable[[str], dict]
) -> TransformReport:
    written = 0
    rows = 0
    with path.open(newline="") as source_file:
        reader = csv.reader(source_file)
        next(reader, None)
        for row in reader:
            rows += 1
            start = datetime.date.fromisoformat(row[2])
            end = datetime.date.fromisoformat(row[3])
            value_type = row[6]
            value = int(row[7]) / 7
            for offset in range((end - start).days + 1):
                date = (start + datetime.timedelta(days=offset)).isoformat()
                target = ensure_record(date)
                if value_type == "Totaal":
                    target["rivm_totaal_personen_getest"] = value
                    target["rivm_aantal_testlabs"] = row[5]
                    written += 2
                elif value_type == "Positief":
                    target["rivm_totaal_personen_positief"] = value
                    written += 1
    return TransformReport("coronawatch_tests", rows, written)


def transform_rivm_tests(
    path: Path, daily: dict, ensure_record: Callable[[str], dict]
) -> TransformReport:
    records = json.loads(path.read_text())
    totals = {}
    positives = {}
    for record in records:
        date = record["Date_of_statistics"]
        totals[date] = totals.get(date, 0) + _integer_or_zero(record["Tested_with_result"])
        positives[date] = positives.get(date, 0) + _integer_or_zero(record["Tested_positive"])
    for date, value in totals.items():
        ensure_record(date)["rivm_totaal_tests"] = value
    for date, value in positives.items():
        ensure_record(date)["rivm_totaal_tests_positief"] = value
    return TransformReport("rivm_tests", len(records), len(totals) + len(positives))


def transform_lcps_legacy(
    path: Path, daily: dict, ensure_record: Callable[[str], dict]
) -> TransformReport:
    rows = 0
    written = 0
    with path.open(newline="") as source_file:
        reader = csv.reader(source_file)
        next(reader, None)
        for row in reader:
            rows += 1
            date = datetime.datetime.strptime(row[0], "%d-%m-%Y").date().isoformat()
            target = ensure_record(date)
            target["nu_op_ic_lcps"] = _integer_or_none(row[1])
            target["nu_op_ic_noncovid_lcps"] = _integer_or_none(row[2])
            target["nu_opgenomen_lcps"] = _integer_or_none(row[3])
            written += 3
    return TransformReport("lcps_legacy_feed", rows, written)


def transform_preserved_sources(
    *, cache_dir: Path, daily: dict, ensure_record: Callable[[str], dict]
) -> list[TransformReport]:
    """Replay preserved, non-network historical sources into the compatibility model."""
    return [
        transform_prevalence(cache_dir / "COVID-19_prevalentie.json", daily),
        transform_legacy_infectieradar(
            cache_dir / "COVID-19_Infectieradar_symptomen_per_dag.json", daily
        ),
        transform_coronawatch_tests(
            cache_dir / "J535D165-RIVM_NL_test_latest.csv", daily, ensure_record
        ),
        transform_rivm_tests(
            cache_dir / "COVID-19_uitgevoerde_testen.json", daily, ensure_record
        ),
        transform_lcps_legacy(cache_dir / "lcps-covid-19.csv", daily, ensure_record),
    ]
