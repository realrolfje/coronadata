from dataclasses import dataclass
import json
from pathlib import Path
from typing import Callable
import urllib.request

from .download import DownloadResult, fetch_csv_source, fetch_json_source
from .erviss import parse as parse_erviss
from .infectieradar_ari import parse as parse_ari
from .models import ParserResult
from .sari import parse as parse_sari
from .variants import parse as parse_variants
from .wastewater import parse as parse_wastewater
from .weekly_trend import parser as weekly_trend_parser


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
        ActiveSourceAdapter("rivm_nice_sari", parse_sari, 1_000),
        ActiveSourceAdapter(
            "rivm_sars_cov_2_wastewater_weekly",
            weekly_trend_parser(
                "rivm_sars_cov_2_wastewater_weekly",
                "sars_cov_2_wastewater_weekly",
                "virus_particles_per_100000_inhabitants",
            ), 1_000,
        ),
        ActiveSourceAdapter(
            "rivm_infectieradar_sars_cov_2_positive",
            weekly_trend_parser(
                "rivm_infectieradar_sars_cov_2_positive",
                "infectieradar_sars_cov_2_positive_percentage",
                "percent_of_participants",
            ), 1_000,
        ),
        ActiveSourceAdapter(
            "rivm_laboratory_sars_cov_2_positive",
            weekly_trend_parser(
                "rivm_laboratory_sars_cov_2_positive",
                "laboratory_sars_cov_2_positive_percentage",
                "percent_of_tested_samples",
            ), 1_000,
        ),
        ActiveSourceAdapter(
            "rivm_laboratory_sars_cov_2_detections",
            weekly_trend_parser(
                "rivm_laboratory_sars_cov_2_detections",
                "laboratory_sars_cov_2_detections_weekly",
                "positive_samples_per_week",
            ), 1_000,
        ),
        ActiveSourceAdapter("ecdc_erviss_nl_sars_cov_2_detections", parse_erviss, 1_000_000),
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
    fetcher = fetch_csv_source if source["format"] == "csv" else fetch_json_source
    url = source["url"]
    if source.get("resource_name"):
        request = urllib.request.Request(url, headers={"User-Agent": "coronadata-source-updater/1"})
        with urllib.request.urlopen(request, timeout=120) as response:
            package = json.load(response)["result"]
        resource = next(
            item for item in package["resources"]
            if item["name"] == source["resource_name"]
        )
        url = resource["url"]
    return fetcher(
        source_id=source_id,
        url=url,
        target=project_root / source["cache_path"],
        snapshot_root=project_root / "cache" / "raw",
        parser=adapter.parser,
        minimum_bytes=adapter.minimum_bytes,
    )


def download_sources(project_root: Path, source_ids=None) -> list[DownloadResult]:
    wanted = list(source_ids or ADAPTERS)
    return [download_source(project_root, source_id) for source_id in wanted]
