import hashlib
import datetime
import json
from pathlib import Path

from .models import Observation, ParserResult


SOURCE_ID = "rivm_variants"
METRIC = "sars_cov_2_variant_cases"
UNIT = "sequenced_samples"
REQUIRED_FIELDS = {
    "Date_of_report", "Date_of_statistics_week_start", "Variant_code",
    "Variant_name", "Sample_size", "Variant_cases", "Is_subvariant_of",
}


def parse(filename):
    path = Path(filename)
    raw = path.read_bytes()
    records = json.loads(raw)
    if not isinstance(records, list) or not records:
        raise ValueError("expected a non-empty JSON array")

    observations = []
    keys = set()
    weeks = set()
    publications = set()
    for index, record in enumerate(records):
        missing = REQUIRED_FIELDS - record.keys()
        if missing:
            raise ValueError(f"record {index} is missing fields: {sorted(missing)}")
        sample_size = record["Sample_size"]
        cases = record["Variant_cases"]
        if not isinstance(sample_size, int) or not isinstance(cases, int):
            raise ValueError(f"record {index} has non-integer counts")
        if sample_size < 0 or cases < 0 or cases > sample_size:
            raise ValueError(f"record {index} has unsafe sample/case counts")
        week = record["Date_of_statistics_week_start"][:10]
        datetime.date.fromisoformat(week)
        key = (week, record["Variant_code"])
        if key in keys:
            raise ValueError(f"duplicate variant/week key: {key}")
        keys.add(key)
        weeks.add(week)
        publication = record["Date_of_report"][:10]
        publications.add(publication)
        observations.append(
            Observation(
                source_id=SOURCE_ID,
                metric=METRIC,
                date=week,
                value=float(cases),
                unit=UNIT,
                publication_date=publication,
                dimensions={
                    "variant_code": record["Variant_code"],
                    "variant_name": record["Variant_name"],
                    "sample_size": sample_size,
                    "is_subvariant_of": record["Is_subvariant_of"],
                },
            )
        )

    return ParserResult(
        source_id=SOURCE_ID,
        observations=observations,
        publication_date=max(publications),
        newest_observation=max(weeks),
        warnings=[],
        provenance={"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(), "record_count": len(records)},
    )
