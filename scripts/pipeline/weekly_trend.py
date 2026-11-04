import csv
import hashlib
from pathlib import Path

from .models import Observation, ParserResult
from .sari import observation_date


def parser(source_id, metric, unit):
    def parse(filename):
        path = Path(filename)
        raw = path.read_bytes()
        observations = []
        seen = set()
        missing_values = 0
        with path.open(newline="", encoding="utf-8-sig") as source_file:
            reader = csv.DictReader(source_file, delimiter=";")
            if set(reader.fieldnames or ()) != {"season", "week", "value"}:
                raise ValueError(f"unexpected {source_id} CSV columns")
            for index, row in enumerate(reader, start=2):
                date = observation_date(row["season"], row["week"])
                if date in seen:
                    raise ValueError(f"duplicate {source_id} week on row {index}: {date}")
                seen.add(date)
                if not row["value"].strip():
                    missing_values += 1
                    continue
                value = float(row["value"].replace(",", "."))
                if value < 0:
                    raise ValueError(f"negative {source_id} value on row {index}")
                observations.append(Observation(
                    source_id=source_id,
                    metric=metric,
                    date=date.isoformat(),
                    value=value,
                    unit=unit,
                    dimensions={"season": row["season"], "week": int(row["week"])},
                ))
        if not observations:
            raise ValueError(f"expected at least one {source_id} observation")
        return ParserResult(
            source_id=source_id,
            observations=observations,
            newest_observation=max(item.date for item in observations),
            warnings=(
                [f"{missing_values} weeks have no reported value"]
                if missing_values else []
            ),
            provenance={"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()},
        )
    return parse
