#!/usr/bin/env python3

import html
import json
from pathlib import Path

from modules.defaults import DAILY_STATS, DOCS_DIR, PROJECT_ROOT
from pipeline.registry import inspect_registry, load_registry
from pipeline.site_export import build_surveillance_export, write_json


def status_page(report):
    rows = []
    for source in report["sources"]:
        messages = " ".join(source["messages"]) or "—"
        rows.append(
            "<tr>"
            f"<td><a href=\"sources/{html.escape(source['id'])}.md\">{html.escape(source['name'])}</a></td>"
            f"<td><span class=\"status status-{html.escape(source['health'])}\">{html.escape(source['health'])}</span></td>"
            f"<td>{html.escape(source['lifecycle'])}</td>"
            f"<td>{html.escape(source.get('newest_observation') or '—')}</td>"
            f"<td>{html.escape(source.get('publication_date') or '—')}</td>"
            f"<td>{html.escape(messages)}</td>"
            "</tr>"
        )
    return f"""<!doctype html>
<html lang=\"nl\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>Bronstatus · Coronadata</title><link rel=\"stylesheet\" href=\"styles.css\"></head>
<body><header class=\"site-header\"><a href=\"index.html\">← Coronadata</a><h1>Bronstatus</h1></header>
<main class=\"page\"><p>Pipeline-status: <strong>{html.escape(report['status'])}</strong>. Dit overzicht is gegenereerd uit het bronnenregister en de lokaal gevalideerde bronbestanden.</p>
<div class=\"table-scroll\"><table class=\"status-table\"><thead><tr><th>Bron</th><th>Status</th><th>Levenscyclus</th><th>Laatste waarneming</th><th>Publicatie</th><th>Toelichting</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<p><a href=\"sources/README.md\">Bronmethodologie</a> · <a href=\"https://github.com/realrolfje/coronadata/blob/master/sources.json\">Machineleesbaar register</a></p></main></body></html>"""


def public_report(report):
    """Remove build-machine details and timestamps that would create meaningless site diffs."""
    fields = (
        "id", "name", "provider", "lifecycle", "required_for_publish",
        "record_count", "publication_date", "newest_observation", "health",
        "messages", "blocking",
    )
    sources = [{field: source.get(field) for field in fields} for source in report["sources"]]
    source_dates = [
        source["publication_date"] or source["newest_observation"]
        for source in sources
        if source["publication_date"] or source["newest_observation"]
    ]
    return {
        "schema_version": 1,
        "status": report["status"],
        "newest_source_date": max(source_dates) if source_dates else None,
        "sources": sources,
    }


def main():
    daily = json.loads(DAILY_STATS.read_text())
    write_json(DOCS_DIR / "data/current-surveillance.json", build_surveillance_export(daily))
    report = inspect_registry(PROJECT_ROOT, load_registry(PROJECT_ROOT / "sources.json"))
    write_json(DOCS_DIR / "data/source-health.json", public_report(report))
    (DOCS_DIR / "source-status.html").write_text(status_page(report))
    print("Generated current-surveillance data and source-status page.")


if __name__ == "__main__":
    main()
