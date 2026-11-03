import csv
import datetime
import hashlib
from pathlib import Path

from .models import Observation, ParserResult


SOURCE_ID = "ecdc_erviss_nl_sars_cov_2_detections"
REQUIRED_FIELDS = {
    "survtype", "countryname", "yearweek", "pathogen", "indicator", "age", "value",
}


def parse(filename):
    path = Path(filename)
    raw = path.read_bytes()
    observations = []
    seen = set()
    with path.open(newline="", encoding="utf-8-sig") as source_file:
        reader = csv.DictReader(source_file)
        missing = REQUIRED_FIELDS - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"ERVISS CSV is missing fields: {sorted(missing)}")
        for index, row in enumerate(reader, start=2):
            if (
                row["countryname"] != "Netherlands"
                or row["pathogen"] != "SARS-CoV-2"
                or row["survtype"] != "non-sentinel"
                or row["indicator"] != "detections"
                or row["age"] != "total"
            ):
                continue
            date = datetime.date.fromisoformat(row["yearweek"])
            if date in seen:
                raise ValueError(f"duplicate ERVISS week on row {index}: {row['yearweek']}")
            seen.add(date)
            value = int(row["value"])
            if value < 0:
                raise ValueError(f"negative ERVISS detections on row {index}")
            observations.append(Observation(
                source_id=SOURCE_ID,
                metric="erviss_sars_cov_2_detections_weekly",
                date=date.isoformat(),
                value=float(value),
                unit="positive_samples_per_week",
                dimensions={"yearweek": row["yearweek"]},
            ))
    if not observations:
        raise ValueError("expected at least one Dutch SARS-CoV-2 ERVISS observation")
    return ParserResult(
        source_id=SOURCE_ID,
        observations=observations,
        newest_observation=max(item.date for item in observations),
        provenance={"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()},
    )
