#!/usr/bin/env python3

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "docs" / "sources"


def text(value, fallback="Not available"):
    if value is None or value == []:
        return fallback
    if isinstance(value, list):
        return ", ".join(f"`{item}`" for item in value)
    return str(value)


def replacement(source):
    lifecycle = source["lifecycle"]
    if source["id"] == "rivm_infectieradar_covid":
        return "Keep this COVID-specific series frozen. ARI Infectieradar is a distinct metric, not a continuation."
    if source["id"].startswith("nice_") or source["id"].startswith("lcps_"):
        return "Keep the COVID hospital series frozen. Current SARI surveillance has a different definition and must not be spliced into it."
    if lifecycle == "active":
        return "Keep and validate before installation."
    if lifecycle == "frozen":
        return "Preserve the final observations and do not request the source during normal builds."
    if lifecycle == "retired":
        return "Do not request the source; retain preserved historical artifacts only."
    return "No replacement is selected; retain only if a consumer and authoritative definition are confirmed."


def render(source):
    known_range = source.get("known_observation_range")
    if known_range:
        observed = f"{known_range[0]} through {known_range[1]}"
    elif source.get("known_last_observation"):
        observed = f"Through {source['known_last_observation']} (start not recorded in the registry)"
    else:
        observed = "Derived from the local cache by `scripts/sourceInventory.py` when actively scanned"
    parser = source.get("parser") or "No parser; source is unused or awaiting a decision"
    cadence = (
        f"Every {source['expected_update_days']} day(s); stale after {source['max_age_days']} day(s)"
        if source.get("expected_update_days") is not None
        else "Ended or not established"
    )
    lines = [
        f"# {source['name']}", "",
        f"- Source ID: `{source['id']}`",
        f"- Owner/provider: {source['provider']}",
        f"- Lifecycle: `{source['lifecycle']}`",
        f"- Purpose/category: {source['category']}",
        f"- Current URL: {source['url']}",
    ]
    if source.get("metadata_url"):
        lines.append(f"- Metadata: {source['metadata_url']}")
    lines.extend([
        f"- URL history: only the current or final known URL is recorded; earlier URLs are not known unless noted below",
        f"- Format: `{source['format']}`",
        f"- Update cadence: {cadence}",
        f"- Observed date range: {observed}",
        f"- Observation date field: `{text(source.get('observation_date_field'))}`",
        f"- Publication date field: `{text(source.get('publication_date_field'))}`",
        f"- Required fields: {text(source.get('required_fields'))}",
        f"- Units: {text(source.get('units'))}",
        f"- Geography: {source['geography']}",
        f"- Parser: `{parser}`",
        f"- Normalized metrics: {text(source.get('metrics'))}",
        f"- Consumers: {text(source.get('consumers'))}",
        "", "## Known gaps and decision", "",
        source.get("notes", "No source-specific gap is recorded beyond the lifecycle and observed range above."),
        "", f"Replacement decision: {replacement(source)}", "",
    ])
    return "\n".join(lines)


def main():
    registry = json.loads((PROJECT_ROOT / "sources.json").read_text())
    OUTPUT.mkdir(parents=True, exist_ok=True)
    index = ["# Source documentation", "", "Generated from `sources.json`.", ""]
    for source in registry["sources"]:
        filename = OUTPUT / f"{source['id']}.md"
        filename.write_text(render(source))
        index.append(
            f"- [{source['name']}]({source['id']}.md) — `{source['lifecycle']}`"
        )
    index.extend([
        "", "## Related decisions", "",
        "- [Current hospital surveillance](hospital-surveillance.md)",
        "- [Source pipeline architecture](../architecture/source-pipeline.md)", "",
    ])
    (OUTPUT / "README.md").write_text("\n".join(index))


if __name__ == "__main__":
    main()
