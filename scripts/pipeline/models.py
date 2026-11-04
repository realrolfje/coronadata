from dataclasses import dataclass, field
from typing import Any


OBSERVATION_STATUSES = {"reported", "revised", "imputed", "calculated"}


@dataclass(frozen=True)
class Observation:
    source_id: str
    metric: str
    date: str
    value: float
    unit: str
    geography: str = "NL"
    publication_date: str | None = None
    dimensions: dict[str, Any] = field(default_factory=dict)
    status: str = "reported"
    schema_version: int = 1
    provenance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.status not in OBSERVATION_STATUSES:
            raise ValueError(f"unsupported observation status: {self.status}")
        if self.schema_version != 1:
            raise ValueError(f"unsupported observation schema version: {self.schema_version}")


@dataclass
class ParserResult:
    source_id: str
    observations: list[Observation]
    publication_date: str | None = None
    newest_observation: str | None = None
    warnings: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
