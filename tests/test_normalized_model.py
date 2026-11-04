import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from pipeline.legacy_daily_stats import parse
from pipeline.models import Observation
from pipeline.storage import SQLiteObservationStore


FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "legacy-daily-stats.json"


class NormalizedModelTest(unittest.TestCase):
    def test_unknown_observation_status_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported observation status"):
            Observation(
                source_id="test", metric="test", date="2024-01-01",
                value=1, unit="count", status="guessed",
            )

    def test_legacy_adapter_preserves_zero_omits_null_and_labels_calculations(self):
        result = parse(FIXTURE)
        by_metric = {}
        for observation in result.observations:
            by_metric.setdefault(observation.metric, []).append(observation)

        self.assertEqual([3.0, 0.0], [item.value for item in by_metric["covid_cases_daily"]])
        self.assertEqual("reported", by_metric["covid_cases_daily"][0].status)
        self.assertEqual("calculated", by_metric["covid_cases_cumulative"][0].status)
        self.assertEqual(1, len(by_metric["covid_reproduction_number"]))
        self.assertEqual("20-29", by_metric["covid_cases_by_age_group"][0].dimensions["age_group"])

    def test_sqlite_persists_schema_status_and_provenance(self):
        result = parse(FIXTURE)
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "normalized.sqlite"
            with SQLiteObservationStore(database) as store:
                store.write(result)
            connection = sqlite3.connect(database)
            row = connection.execute(
                """
                SELECT schema_version, status, provenance_json
                FROM observations WHERE metric = 'covid_cases_cumulative'
                ORDER BY observation_date LIMIT 1
                """
            ).fetchone()
            connection.close()

        self.assertEqual(1, row[0])
        self.assertEqual("calculated", row[1])
        provenance = json.loads(row[2])
        self.assertEqual("legacy_daily_stats", provenance["transformer"])
        self.assertEqual("totaal_positief", provenance["legacy_field"])


if __name__ == "__main__":
    unittest.main()
