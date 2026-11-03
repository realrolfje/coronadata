from dataclasses import dataclass, field
import time

from modules.defaults import CACHE_DIR, DAILY_STATS, PROJECT_ROOT
from modules.download_infectieradar_ari import store as store_ari
from modules.download_rioolwaterdata import store as store_wastewater
from modules.download_varianten import store as store_variants
from modules.metenisweten import initrecord, metenisweten, writeMetenIsWeten

from .active_sources import download_sources
from .calculations import CalculationReport, run_calculations
from .download import DownloadResult
from .legacy_transform import TransformReport, transform_preserved_sources


@dataclass
class PipelineReport:
    downloads: list[DownloadResult] = field(default_factory=list)
    transformations: list[TransformReport] = field(default_factory=list)
    calculations: list[CalculationReport] = field(default_factory=list)
    active_transforms: dict[str, bool] = field(default_factory=dict)
    persisted: bool = False

    @property
    def changed(self):
        return any(result.changed for result in self.downloads) or any(
            self.active_transforms.values()
        )


ACTIVE_STORES = {
    "rivm_wastewater": store_wastewater,
    "rivm_variants": store_variants,
    "rivm_infectieradar_ari": store_ari,
    # The SARI graph consumes the validated CSV directly; it is deliberately
    # not folded into the legacy COVID daily model.
    "rivm_nice_sari": lambda path: False,
    "rivm_sars_cov_2_wastewater_weekly": lambda path: False,
    "rivm_infectieradar_sars_cov_2_positive": lambda path: False,
    "rivm_laboratory_sars_cov_2_positive": lambda path: False,
    "rivm_laboratory_sars_cov_2_detections": lambda path: False,
    "ecdc_erviss_nl_sars_cov_2_detections": lambda path: False,
}


def download_stage(source_ids=None) -> list[DownloadResult]:
    """Stage 1: download and validate active sources without transforming graph data."""
    return download_sources(PROJECT_ROOT, source_ids)


def transform_active_stage(
    downloads: list[DownloadResult], *, force=False
) -> dict[str, bool]:
    """Stage 2a: apply source-specific adapters to the compatibility model."""
    transformed = {}
    baseline_mtime = DAILY_STATS.stat().st_mtime if DAILY_STATS.exists() else 0
    for result in downloads:
        should_transform = (
            force or result.changed or result.target.stat().st_mtime > baseline_mtime
        )
        transformed[result.source_id] = (
            ACTIVE_STORES[result.source_id](result.target) if should_transform else False
        )
    return transformed


def transform_preserved_stage() -> list[TransformReport]:
    """Stage 2b: replay preserved ended feeds; this performs no network access."""
    return transform_preserved_sources(
        cache_dir=CACHE_DIR, daily=metenisweten, ensure_record=initrecord
    )


def calculation_stage() -> list[CalculationReport]:
    """Stage 3: run cross-source calculations only after transformations complete."""
    return run_calculations(metenisweten)


def storage_stage() -> None:
    """Stage 4: persist the compatibility model. Normalized storage is rebuilt separately."""
    writeMetenIsWeten()


def run_update_pipeline(*, source_ids=None, force=False) -> PipelineReport:
    report = PipelineReport()
    report.downloads = download_stage(source_ids)
    report.active_transforms = transform_active_stage(report.downloads, force=force)
    needs_rebuild = force or any(report.active_transforms.values()) or not DAILY_STATS.exists()
    if needs_rebuild:
        report.transformations = transform_preserved_stage()
        report.calculations = calculation_stage()
        storage_stage()
        report.persisted = True
    return report


def cache_is_recent(seconds=1200):
    return DAILY_STATS.exists() and DAILY_STATS.stat().st_mtime > time.time() - seconds
