from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from pipeline.storage import MemoryObservationStore, SQLiteObservationStore
from pipeline.wastewater import METRIC, SOURCE_ID, parse
from pipeline.infectieradar_ari import parse as parse_ari
from pipeline.variants import parse as parse_variants


FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "wastewater.json"
FIXTURES = PROJECT_ROOT / "tests" / "fixtures"


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

    def test_variants_parser_validates_and_normalizes(self):
        result = parse_variants(FIXTURES / "variants.json")

        self.assertEqual(result.source_id, "rivm_variants")
        self.assertEqual(result.publication_date, "2026-10-28")
        self.assertEqual(result.newest_observation, "2026-10-19")
        self.assertEqual(len(result.observations), 2)
        self.assertEqual(result.observations[0].dimensions["sample_size"], 100)

    def test_ari_parser_preserves_missing_value_as_gap(self):
        result = parse_ari(FIXTURES / "infectieradar-ari.json")

        self.assertEqual(result.source_id, "rivm_infectieradar_ari")
        self.assertEqual(result.newest_observation, "2026-10-27")
        self.assertEqual(len(result.observations), 2)
        self.assertIn("1 dates have no reported ARI percentage", result.warnings)


if __name__ == "__main__":
    unittest.main()
