import csv
import datetime
import json
from pathlib import Path


LIFECYCLE_STATES = {"active", "frozen", "retired", "broken", "unknown"}
REQUIRED_SOURCE_KEYS = {
    "id",
    "name",
    "provider",
    "category",
    "lifecycle",
    "required_for_publish",
    "url",
    "cache_path",
    "format",
    "parser",
    "expected_update_days",
    "max_age_days",
    "observation_date_field",
    "publication_date_field",
    "required_fields",
    "units",
    "geography",
    "metrics",
    "consumers",
}


def load_registry(filename):
    path = Path(filename)
    registry = json.loads(path.read_text())
    validate_registry(registry)
    return registry


def validate_registry(registry):
    if registry.get("schema_version") != 1:
        raise ValueError("unsupported source registry schema version")
    sources = registry.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("source registry must contain a non-empty sources list")

    ids = set()
    for source in sources:
        missing = REQUIRED_SOURCE_KEYS - source.keys()
        if missing:
            raise ValueError(f"source {source.get('id')} is missing keys: {sorted(missing)}")
        if source["id"] in ids:
            raise ValueError(f"duplicate source id: {source['id']}")
        ids.add(source["id"])
        if source["lifecycle"] not in LIFECYCLE_STATES:
            raise ValueError(
                f"source {source['id']} has invalid lifecycle {source['lifecycle']}"
            )
        if source["required_for_publish"] and source["lifecycle"] != "active":
            raise ValueError(
                f"required source {source['id']} must have active lifecycle"
            )


def parse_date(value):
    if value is None:
        return None
    text = str(value).strip()
    candidates = (text[:10], text)
    for candidate in candidates:
        try:
            return datetime.date.fromisoformat(candidate)
        except ValueError:
            pass
        try:
            return datetime.datetime.strptime(candidate, "%d-%m-%Y").date()
        except ValueError:
            pass
    return None


def inspect_json(path, source):
    records = json.loads(path.read_bytes())
    if not isinstance(records, list) or not records:
        raise ValueError("expected a non-empty JSON array")

    required_fields = set(source["required_fields"])
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"record {index} is not an object")
        missing = required_fields - record.keys()
        if missing:
            raise ValueError(f"record {index} is missing fields: {sorted(missing)}")

    def latest(field):
        if not field:
            return None
        dates = [parse_date(record.get(field)) for record in records]
        dates = [date for date in dates if date is not None]
        return max(dates) if dates else None

    return {
        "record_count": len(records),
        "newest_observation": latest(source["observation_date_field"]),
        "publication_date": latest(source["publication_date_field"]),
    }


def inspect_csv(path, source):
    with path.open(newline="") as source_file:
        sample = source_file.read(4096)
        source_file.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",;")
        reader = csv.DictReader(source_file, dialect=dialect)
        fields = set(reader.fieldnames or [])
        missing = set(source["required_fields"]) - fields
        if missing:
            raise ValueError(f"CSV is missing fields: {sorted(missing)}")
        records = list(reader)

    field = source["observation_date_field"]
    if field == "season/week":
        from .sari import observation_date
        dates = [
            observation_date(record["season"], record["week"])
            for record in records
            if record.get("value", "").strip()
        ]
    else:
        dates = [parse_date(record.get(field)) for record in records] if field else []
    dates = [date for date in dates if date is not None]
    return {
        "record_count": len(records),
        "newest_observation": max(dates) if dates else None,
        "publication_date": None,
    }


def inspect_source(project_root, source, today=None):
    today = today or datetime.date.today()
    result = {
        "id": source["id"],
        "name": source["name"],
        "provider": source["provider"],
        "lifecycle": source["lifecycle"],
        "required_for_publish": source["required_for_publish"],
        "cache_path": source["cache_path"],
        "cache_exists": False,
        "cache_size": None,
        "cache_modified_at": None,
        "record_count": None,
        "publication_date": None,
        "newest_observation": source.get("known_last_observation"),
        "health": source["lifecycle"],
        "messages": [],
        "blocking": False,
    }

    cache_path = source["cache_path"]
    if not cache_path:
        result["health"] = "not_configured" if source["lifecycle"] == "active" else source["lifecycle"]
        result["messages"].append("No local cache path is configured.")
        return result

    path = project_root / cache_path
    if not path.exists():
        result["health"] = "missing"
        result["messages"].append("Local cache file is missing.")
        result["blocking"] = bool(source["required_for_publish"])
        return result

    stat = path.stat()
    result["cache_exists"] = True
    result["cache_size"] = stat.st_size
    result["cache_modified_at"] = datetime.datetime.fromtimestamp(
        stat.st_mtime, datetime.timezone.utc
    ).isoformat()

    should_scan = source["lifecycle"] == "active" and source.get("scan_cache", True)
    if should_scan and source["format"] in {"json", "csv"}:
        try:
            details = (
                inspect_json(path, source)
                if source["format"] == "json"
                else inspect_csv(path, source)
            )
            result.update(
                {
                    key: value.isoformat() if isinstance(value, datetime.date) else value
                    for key, value in details.items()
                }
            )
        except (OSError, ValueError, json.JSONDecodeError, csv.Error) as error:
            result["health"] = "invalid"
            result["messages"].append(str(error))
            result["blocking"] = bool(source["required_for_publish"])
            return result

    if source["lifecycle"] == "active":
        freshness_value = result["publication_date"] or result["newest_observation"]
        freshness_date = parse_date(freshness_value)
        max_age = source["max_age_days"]
        if max_age is not None and freshness_date is not None:
            age = (today - freshness_date).days
            if age > max_age:
                result["health"] = "stale"
                result["messages"].append(
                    f"Newest source date is {age} days old; maximum is {max_age}."
                )
                result["blocking"] = bool(source["required_for_publish"])
            else:
                result["health"] = "healthy"
        elif result["health"] == "active":
            result["health"] = "unverified"

    return result


def inspect_registry(project_root, registry, today=None):
    sources = [
        inspect_source(project_root, source, today=today)
        for source in registry["sources"]
    ]
    return {
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "blocked" if any(source["blocking"] for source in sources) else "healthy",
        "sources": sources,
    }


def markdown_report(report):
    lines = [
        "# Source health",
        "",
        "Generated from `sources.json` by `scripts/sourceInventory.py`.",
        "",
        f"Overall status: **{report['status']}**",
        "",
        "| Source | Lifecycle | Health | Newest observation | Publication | Cache |",
        "|---|---|---|---|---|---|",
    ]
    for source in report["sources"]:
        cache = source["cache_path"] or "—"
        lines.append(
            "| {name} | {lifecycle} | {health} | {observation} | {publication} | `{cache}` |".format(
                name=source["name"],
                lifecycle=source["lifecycle"],
                health=source["health"],
                observation=source["newest_observation"] or "—",
                publication=source["publication_date"] or "—",
                cache=cache,
            )
        )
    lines.extend(["", "## Details", ""])
    for source in report["sources"]:
        if source["messages"]:
            lines.append(f"- **{source['id']}**: {' '.join(source['messages'])}")
    lines.append("")
    return "\n".join(lines)
