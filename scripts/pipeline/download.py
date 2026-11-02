from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import shutil
import tempfile
from typing import Callable
import urllib.request

from .models import ParserResult


@dataclass(frozen=True)
class DownloadResult:
    source_id: str
    target: Path
    snapshot: Path
    changed: bool
    parser_result: ParserResult
    content_type: str
    byte_count: int
    sha256: str


def fetch_source(
    *,
    source_id: str,
    url: str,
    target: Path,
    snapshot_root: Path,
    parser: Callable[[Path], ParserResult],
    minimum_bytes: int,
    accepted_content_types: set[str],
    expected_content_description: str,
    suffix: str,
    timeout: int = 120,
) -> DownloadResult:
    """Download, validate and atomically install one JSON source."""
    target = Path(target)
    snapshot_root = Path(snapshot_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    snapshot_root.mkdir(parents=True, exist_ok=True)

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "coronadata-source-updater/1"},
    )
    temporary_name = None
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", 200)
            if status != 200:
                raise ValueError(f"{source_id}: expected HTTP 200, received {status}")
            content_type = response.headers.get_content_type()
            if content_type not in accepted_content_types:
                raise ValueError(
                    f"{source_id}: expected {expected_content_description} content type, received {content_type}"
                )
            with tempfile.NamedTemporaryFile(
                mode="wb", prefix=f"{source_id}-", suffix=suffix, delete=False,
                dir=target.parent,
            ) as temporary:
                temporary_name = temporary.name
                shutil.copyfileobj(response, temporary)

        temporary_path = Path(temporary_name)
        byte_count = temporary_path.stat().st_size
        if byte_count < minimum_bytes:
            raise ValueError(
                f"{source_id}: received {byte_count} bytes; minimum is {minimum_bytes}"
            )

        parser_result = parser(temporary_path)
        digest = hashlib.sha256(temporary_path.read_bytes()).hexdigest()
        existing_digest = (
            hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None
        )
        publication = parser_result.publication_date or "unknown-date"
        snapshot = snapshot_root / source_id / f"{publication}-{digest[:12]}{suffix}"
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        if not snapshot.exists():
            shutil.copyfile(temporary_path, snapshot)
            snapshot.chmod(0o444)

        changed = digest != existing_digest
        if changed:
            os.replace(temporary_path, target)
            temporary_name = None

        return DownloadResult(
            source_id=source_id,
            target=target,
            snapshot=snapshot,
            changed=changed,
            parser_result=parser_result,
            content_type=content_type,
            byte_count=byte_count,
            sha256=digest,
        )
    finally:
        if temporary_name:
            Path(temporary_name).unlink(missing_ok=True)


def fetch_json_source(**kwargs) -> DownloadResult:
    return fetch_source(
        **kwargs,
        accepted_content_types={"application/json", "text/json"},
        expected_content_description="JSON",
        suffix=".json",
    )


def fetch_csv_source(**kwargs) -> DownloadResult:
    return fetch_source(
        **kwargs,
        accepted_content_types={"text/csv", "text/plain", "application/octet-stream"},
        expected_content_description="CSV",
        suffix=".csv",
    )
