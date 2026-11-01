import hashlib
import json
from pathlib import Path

from .models import Observation, ParserResult


SOURCE_ID = "rivm_wastewater"
METRIC = "wastewater_rna_flow_per_100000"
UNIT = "virus_particles_per_100000_inhabitants"
REQUIRED_FIELDS = {
    "Date_measurement",
    "Date_of_report",
    "RNA_flow_per_100000",
    "RWZI_AWZI_code",
    "RWZI_AWZI_name",
}


def parse(filename):
    path = Path(filename)
    raw = path.read_bytes()
    records = json.loads(raw)
    warnings = []
    observations = []
    publication_dates = []

    for index, record in enumerate(records):
        missing = REQUIRED_FIELDS - record.keys()
        if missing:
            raise ValueError(f"record {index} is missing fields: {sorted(missing)}")
        value = record["RNA_flow_per_100000"]
        if value is None:
            warnings.append(f"record {index} has no RNA flow value")
            continue
        if float(value) < 0:
            raise ValueError(f"record {index} has a negative RNA flow value")

        date = record["Date_measurement"][:10]
        publication_date = record["Date_of_report"][:10]
        publication_dates.append(publication_date)
        observations.append(
            Observation(
                source_id=SOURCE_ID,
                metric=METRIC,
                date=date,
                value=float(value),
                unit=UNIT,
                geography=f"RWZI:{record['RWZI_AWZI_code']}",
                publication_date=publication_date,
                dimensions={"name": record["RWZI_AWZI_name"]},
            )
        )

    dates = [observation.date for observation in observations]
    return ParserResult(
        source_id=SOURCE_ID,
        observations=observations,
        publication_date=max(publication_dates) if publication_dates else None,
        newest_observation=max(dates) if dates else None,
        warnings=warnings,
        provenance={
            "path": str(path),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "record_count": len(records),
        },
    )
