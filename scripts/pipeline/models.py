from dataclasses import dataclass, field
from typing import Any


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


@dataclass
class ParserResult:
    source_id: str
    observations: list[Observation]
    publication_date: str | None = None
    newest_observation: str | None = None
    warnings: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
