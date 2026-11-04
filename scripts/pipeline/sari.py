import csv
import datetime
import hashlib
from pathlib import Path

from .models import Observation, ParserResult


SOURCE_ID = "rivm_nice_sari"


def observation_date(season, week):
    first_year, second_year = (int(value) for value in season.split("/"))
    year = first_year if int(week) >= 40 else second_year
    return datetime.date.fromisocalendar(year, int(week), 1)


def parse(filename):
    path = Path(filename)
    raw = path.read_bytes()
    observations = []
    seen = set()
    with path.open(newline="", encoding="utf-8-sig") as source_file:
        reader = csv.DictReader(source_file, delimiter=";")
        if set(reader.fieldnames or ()) != {"season", "value", "week"}:
            raise ValueError("unexpected RIVM SARI CSV columns")
        for index, row in enumerate(reader, start=2):
            date = observation_date(row["season"], row["week"])
            if date in seen:
                raise ValueError(f"duplicate SARI week on row {index}: {date}")
            seen.add(date)
            value = int(row["value"])
            if value < 0:
                raise ValueError(f"negative SARI admissions on row {index}")
            observations.append(Observation(
                source_id=SOURCE_ID,
                metric="sari_icu_admissions_weekly",
                date=date.isoformat(),
                value=float(value),
                unit="admissions_per_week",
                dimensions={"season": row["season"], "week": int(row["week"])},
            ))
    if not observations:
        raise ValueError("expected at least one SARI observation")
    newest = max(item.date for item in observations)
    return ParserResult(
        source_id=SOURCE_ID,
        observations=observations,
        newest_observation=newest,
        provenance={"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()},
    )
