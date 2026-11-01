from dataclasses import dataclass
import json
from pathlib import Path
from typing import Callable

from .download import DownloadResult, fetch_json_source
from .infectieradar_ari import parse as parse_ari
from .models import ParserResult
from .variants import parse as parse_variants
from .wastewater import parse as parse_wastewater


@dataclass(frozen=True)
class ActiveSourceAdapter:
    source_id: str
    parser: Callable[[Path], ParserResult]
    minimum_bytes: int


ADAPTERS = {
    adapter.source_id: adapter
    for adapter in (
        ActiveSourceAdapter("rivm_wastewater", parse_wastewater, 1_000_000),
        ActiveSourceAdapter("rivm_variants", parse_variants, 100_000),
        ActiveSourceAdapter("rivm_infectieradar_ari", parse_ari, 10_000),
    )
}


def load_active_sources(project_root: Path) -> dict[str, dict]:
    registry = json.loads((project_root / "sources.json").read_text())
    return {
        source["id"]: source
        for source in registry["sources"]
        if source["id"] in ADAPTERS
    }


def download_source(project_root: Path, source_id: str) -> DownloadResult:
    sources = load_active_sources(project_root)
    if source_id not in sources:
        raise ValueError(f"unknown active source: {source_id}")
    source = sources[source_id]
    adapter = ADAPTERS[source_id]
    return fetch_json_source(
        source_id=source_id,
        url=source["url"],
        target=project_root / source["cache_path"],
        snapshot_root=project_root / "cache" / "raw",
        parser=adapter.parser,
        minimum_bytes=adapter.minimum_bytes,
    )


def download_sources(project_root: Path, source_ids=None) -> list[DownloadResult]:
    wanted = list(source_ids or ADAPTERS)
    return [download_source(project_root, source_id) for source_id in wanted]
