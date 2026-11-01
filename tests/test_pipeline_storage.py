from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from pipeline.storage import MemoryObservationStore, SQLiteObservationStore
from pipeline.wastewater import METRIC, SOURCE_ID, parse


FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "wastewater.json"


class PipelineStorageTest(unittest.TestCase):
    def test_wastewater_parser_returns_common_result(self):
        result = parse(FIXTURE)
        self.assertEqual(SOURCE_ID, result.source_id)
        self.assertEqual("2024-10-04", result.publication_date)
        self.assertEqual("2024-10-01", result.newest_observation)
        self.assertEqual(3, len(result.observations))
        self.assertEqual([], result.warnings)

    def test_memory_and_sqlite_queries_match(self):
        result = parse(FIXTURE)
        memory = MemoryObservationStore()
        self.assertEqual(3, memory.write(result))

        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "observations.sqlite"
            with SQLiteObservationStore(database) as sqlite_store:
                sqlite_store.write(result)
                self.assertEqual(0, sqlite_store.write(result))
                sqlite_values = sqlite_store.daily_average(SOURCE_ID, METRIC)

        expected = [("2024-09-30", 200.0), ("2024-10-01", 200.0)]
        self.assertEqual(expected, memory.daily_average(SOURCE_ID, METRIC))
        self.assertEqual(expected, sqlite_values)


if __name__ == "__main__":
    unittest.main()
