from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class SeriesDefinition:
    key: str
    label: str
    unit: str
    status: str
    source_id: str


WASTEWATER_SERIES = (
    SeriesDefinition(
        "wastewater_rna", "Virusdeeltjes per 100.000 inwoners", "virusdeeltjes",
        "reported", "rivm_wastewater",
    ),
    SeriesDefinition(
        "estimated_infectious", "Geschat aantal besmettelijke mensen", "personen",
        "calculated", "derived_coronadata",
    ),
)


def _number(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_surveillance_export(daily: dict) -> dict:
    observations = []
    for date, record in sorted(daily.items()):
        rna = record.get("RNA") or {}
        wastewater = _number(rna.get("RNA_per_100k_avg"))
        estimated = _number(rna.get("besmettelijk"))
        if not wastewater and not estimated:
            continue
        observations.append(
            {
                "date": date,
                "wastewater_rna": wastewater if wastewater else None,
                "estimated_infectious": estimated if estimated else None,
            }
        )
    newest = observations[-1]["date"] if observations else None
    return {
        "schema_version": 1,
        "title": "SARS-CoV-2 in rioolwater",
        "newest_observation": newest,
        "series": [definition.__dict__ for definition in WASTEWATER_SERIES],
        "observations": observations,
    }


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
