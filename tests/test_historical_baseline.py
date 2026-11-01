import datetime
import hashlib
import json
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "daily-stats.json"
BASELINE_FILE = PROJECT_ROOT / "tests" / "fixtures" / "historical-baseline.json"


def nested_value(record, field):
    value = record
    for part in field.split("."):
        value = value.get(part)
        if value is None:
            return None
    return value


class HistoricalBaselineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_bytes = DATA_FILE.read_bytes()
        cls.data = json.loads(cls.original_bytes)
        cls.baseline = json.loads(BASELINE_FILE.read_text())

    @classmethod
    def tearDownClass(cls):
        current_digest = hashlib.sha256(DATA_FILE.read_bytes()).hexdigest()
        original_digest = hashlib.sha256(cls.original_bytes).hexdigest()
        if current_digest != original_digest:
            raise AssertionError("historical baseline was modified while testing")

    def test_file_digest(self):
        digest = hashlib.sha256(self.original_bytes).hexdigest()
        self.assertEqual(self.baseline["sha256"], digest)

    def test_date_bounds_and_record_count(self):
        dates = list(self.data)
        self.assertEqual(self.baseline["record_count"], len(dates))
        self.assertEqual(self.baseline["first_date"], dates[0])
        self.assertEqual(self.baseline["last_date"], dates[-1])

    def test_graph_date_range(self):
        first = max(
            datetime.date.fromisoformat(self.baseline["first_date"]),
            datetime.date(2020, 3, 1),
        )
        last_observation = datetime.date.fromisoformat(self.baseline["last_date"])
        last = last_observation + datetime.timedelta(days=6)
        self.assertEqual(
            self.baseline["graph_date_range"],
            {"first_date": first.isoformat(), "last_date": last.isoformat()},
        )

    def test_latest_observations(self):
        for expected in self.baseline["latest_observations"]:
            with self.subTest(field=expected["field"]):
                observations = [
                    (date, nested_value(record, expected["field"]))
                    for date, record in self.data.items()
                ]
                observations = [
                    item for item in observations if item[1] is not None and item[1] != 0
                ]
                self.assertTrue(observations)
                self.assertEqual(
                    (expected["date"], expected["value"]), observations[-1]
                )


if __name__ == "__main__":
    unittest.main()
