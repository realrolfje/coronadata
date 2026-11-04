import datetime
import hashlib
import json
from pathlib import Path

from .models import Observation, ParserResult


SOURCE_ID = "rivm_infectieradar_ari"
METRIC = "infectieradar_ari_symptoms_percentage"
UNIT = "percent_of_participants"
REQUIRED_FIELDS = {"Date_of_report", "Date_of_statistics"}


def parse(filename):
    path = Path(filename)
    raw = path.read_bytes()
    records = json.loads(raw)
    if not isinstance(records, list) or not records:
        raise ValueError("expected a non-empty JSON array")

    observations = []
    dates = set()
    publications = set()
    for index, record in enumerate(records):
        missing = REQUIRED_FIELDS - record.keys()
        if missing:
            raise ValueError(f"record {index} is missing fields: {sorted(missing)}")
        date = record["Date_of_statistics"][:10]
        datetime.date.fromisoformat(date)
        if date in dates:
            raise ValueError(f"duplicate ARI observation date: {date}")
        dates.add(date)
        value = record.get("Perc_ARI_symptoms")
        if value is None:
            continue
        if not isinstance(value, (int, float)) or not 0 <= value <= 100:
            raise ValueError(f"record {index} has an invalid ARI percentage")
        publication = record["Date_of_report"][:10]
        publications.add(publication)
        observations.append(
            Observation(
                source_id=SOURCE_ID,
                metric=METRIC,
                date=date,
                value=float(value),
                unit=UNIT,
                publication_date=publication,
            )
        )

    ordered = sorted(datetime.date.fromisoformat(value) for value in dates)
    gaps = [(right - left).days for left, right in zip(ordered, ordered[1:])]
    missing_values = len(records) - len(observations)
    warnings = []
    if missing_values:
        warnings.append(f"{missing_values} dates have no reported ARI percentage")
    if gaps and max(gaps) > 7:
        warnings.append(f"largest reported-date gap is {max(gaps)} days")
    return ParserResult(
        source_id=SOURCE_ID,
        observations=observations,
        publication_date=max(publications),
        newest_observation=max(dates),
        warnings=warnings,
        provenance={"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(), "record_count": len(records)},
    )
