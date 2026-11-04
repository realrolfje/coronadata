import datetime
import json
import tempfile
import unittest
from pathlib import Path

from pipeline.registry import inspect_csv, inspect_source, load_registry, validate_registry


class SourceRegistryTest(unittest.TestCase):
    def test_repository_registry_is_valid(self):
        project_root = Path(__file__).resolve().parents[1]
        registry = load_registry(project_root / "sources.json")

        self.assertGreaterEqual(len(registry["sources"]), 18)
        self.assertEqual(
            len({source["id"] for source in registry["sources"]}),
            len(registry["sources"]),
        )

    def test_duplicate_source_ids_are_rejected(self):
        source = self._source()
        with self.assertRaisesRegex(ValueError, "duplicate source id"):
            validate_registry(
                {"schema_version": 1, "sources": [source, dict(source)]}
            )

    def test_newest_source_date_controls_freshness(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_root = Path(temporary_directory)
            cache = project_root / "sample.json"
            cache.write_text(
                json.dumps(
                    [
                        {
                            "observed": "2026-10-10",
                            "published": "2026-10-11",
                            "value": 12,
                        }
                    ]
                )
            )
            source = self._source()
            source["cache_path"] = "sample.json"

            healthy = inspect_source(
                project_root, source, today=datetime.date(2026, 10, 20)
            )
            stale = inspect_source(
                project_root, source, today=datetime.date(2026, 11, 1)
            )

            self.assertEqual(healthy["health"], "healthy")
            self.assertEqual(stale["health"], "stale")
            self.assertTrue(stale["blocking"])

    def test_future_empty_season_weeks_are_not_observations(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "trend.csv"
            path.write_text(
                "season;week;value\n"
                "2026/2027;43;1.2\n"
                "2026/2027;39;\n"
            )
            source = self._source()
            source.update({
                "format": "csv",
                "required_fields": ["season", "week", "value"],
                "observation_date_field": "season/week",
                "publication_date_field": None,
            })
            details = inspect_csv(path, source)
        self.assertEqual(datetime.date(2026, 10, 19), details["newest_observation"])

    @staticmethod
    def _source():
        return {
            "id": "sample",
            "name": "Sample",
            "provider": "Test provider",
            "category": "test",
            "lifecycle": "active",
            "required_for_publish": True,
            "url": "https://example.invalid/sample.json",
            "cache_path": "sample.json",
            "format": "json",
            "parser": "sample.parser",
            "expected_update_days": 7,
            "max_age_days": 14,
            "observation_date_field": "observed",
            "publication_date_field": "published",
            "required_fields": ["observed", "published", "value"],
            "units": ["count"],
            "geography": "test",
            "metrics": ["sample"],
            "consumers": ["sample.py"],
        }


if __name__ == "__main__":
    unittest.main()
